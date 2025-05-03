import typing

from sqlglot import parse_one, expressions as sg, errors as sg_errors

from statql.common import FrozenModel
from ..common import (
    Term,
    ScalarFunction,
    AggregationFunction,
    TableColumn,
    AggregationFunctionNames,
    ScalarFunctionNames,
    Constant,
    BinaryBooleanExpression,
    BooleanBinaryOperators,
    BooleanExpression,
    StatQLContext,
)
from ..logic import get_scalar_function_cls


class From(FrozenModel):
    catalog_name: str
    table_path: typing.Sequence[str]


class Where(FrozenModel):
    condition: BooleanExpression


class OrderBy(FrozenModel):
    term: Term
    desc: bool


class ParsedQuery(FrozenModel):
    alias_to_term: typing.Mapping[str, Term]
    from_: From
    where: BooleanExpression | None
    group_bys: typing.AbstractSet[Term]
    order_by: OrderBy | None
    limit: int | None


class QueryParser:
    @classmethod
    def parse(cls, *, sql: str, ctx: StatQLContext) -> ParsedQuery:
        try:
            root_expression = parse_one(sql=sql)
        except sg_errors.ParseError as e:
            raise SyntaxError(f"Failed to parse SQL") from e

        if not isinstance(root_expression, sg.Select):
            raise SyntaxError(f"Unsupported root expression type: {type(root_expression).__name__}")

        cls._check_for_unsupported_expressions(root_expression=root_expression)

        from_expression = root_expression.args.get("from")

        if not isinstance(from_expression, sg.From):
            raise SyntaxError(f"Unexpected from expression type: {type(from_expression).__name__}")

        from_ = cls._parse_from(from_expression=from_expression)

        if from_.catalog_name not in ctx.catalogs:
            raise SyntaxError(f"Catalog not found: {from_.catalog_name}")

        alias_to_term = cls._parse_terms(selects=root_expression.selects)

        if where := root_expression.args.get("where"):
            where = cls._parse_bool_expression(exp=where.this)
        else:
            where = None

        if group_bys := root_expression.args.get("group"):
            group_bys = cls._parse_group_by(group_by=group_bys, alias_to_term=alias_to_term)
        else:
            group_bys = set()

        if order_by := root_expression.args.get("order"):
            order_by = cls._parse_order_by(order_by=order_by, alias_to_term=alias_to_term)
        else:
            order_by = None

        if limit := root_expression.args.get("limit"):
            limit = cls._parse_limit(limit=limit)
        else:
            limit = None

        return ParsedQuery(alias_to_term=alias_to_term, from_=from_, where=where, group_bys=group_bys, order_by=order_by, limit=limit)

    @classmethod
    def _check_for_unsupported_expressions(cls, *, root_expression: sg.Select):
        # Checking for unsupported expressions
        if root_expression.args.get("joins"):
            raise SyntaxError(f"JOIN is not supported")

        if root_expression.args.get("having"):
            raise SyntaxError(f"HAVING is not supported")

    @classmethod
    def _parse_terms(cls, *, selects: typing.Iterable[sg.Expression]) -> typing.Dict[str, Term]:
        alias_to_term = {}

        for select in selects:
            if isinstance(select, sg.Alias):
                term = cls._parse_term(exp=select.this)
                alias_to_term[select.alias] = term
            else:
                term = cls._parse_term(exp=select)
                alias_to_term[term.get_name()] = term

        return alias_to_term

    @classmethod
    def _parse_from(cls, *, from_expression: sg.From) -> From:
        target = from_expression.this

        if not isinstance(target, sg.Table):
            raise SyntaxError(f"Unexpected from expression target type: {type(target).__name__}")

        target_parts = target.sql().split(".")

        if len(target_parts) < 2:
            raise SyntaxError(f"Invalid target: {target.sql()}")

        return From(catalog_name=target_parts[0], table_path=target_parts[1:])

    @classmethod
    def _parse_term(cls, *, exp: sg.Expression) -> Term:
        # TODO - stop this monstrosity, functions should be defined in one placed and parsed dynamically!
        if isinstance(exp, sg.Count):
            if exp.this:
                argument = cls._parse_term(exp=exp.this)
                return AggregationFunction(func_name=AggregationFunctionNames.COUNT, argument=argument)
            else:
                return AggregationFunction(func_name=AggregationFunctionNames.COUNT, argument=None)

        elif isinstance(exp, sg.Sum):
            if not exp.this:
                raise SyntaxError("SUM must receive an argument")

            argument = cls._parse_term(exp=exp.this)
            return AggregationFunction(func_name=AggregationFunctionNames.SUM, argument=argument)

        elif isinstance(exp, sg.Avg):
            if not exp.this:
                raise SyntaxError("AVG must receive an argument")

            argument = cls._parse_term(exp=exp.this)
            return AggregationFunction(func_name=AggregationFunctionNames.AVG, argument=argument)

        elif isinstance(exp, sg.Split):
            to_split = exp.this
            split_by = exp.expression

            if not to_split or not split_by:
                raise SyntaxError("Split is missing arguments")

            return ScalarFunction(func_name=ScalarFunctionNames.SPLIT, arguments=(cls._parse_term(exp=to_split), cls._parse_term(exp=split_by)))

        elif isinstance(exp, sg.Concat):
            arguments = [cls._parse_term(exp=arg_exp) for arg_exp in exp.expressions]
            return ScalarFunction(func_name=ScalarFunctionNames.CONCAT, arguments=tuple(arguments))

        elif isinstance(exp, sg.Anonymous):
            if not exp.this:
                raise ValueError(f"`Anonymous` is missing `this`")

            try:
                scalar_func_name = ScalarFunctionNames(exp.this)
            except ValueError as e:
                raise SyntaxError(f"Unknown scalar function: {exp.this}") from e

            scalar_func_cls = get_scalar_function_cls(func_name=scalar_func_name)

            if len(exp.expressions) != scalar_func_cls.num_args:
                raise SyntaxError(f"Scalar function {scalar_func_name} expects {scalar_func_cls.num_args} args")

            arguments = [cls._parse_term(exp=arg_exp) for arg_exp in exp.expressions]
            return ScalarFunction(func_name=scalar_func_name, arguments=tuple(arguments))

        elif isinstance(exp, sg.Column):
            return TableColumn(column_name=exp.this.name)

        elif isinstance(exp, sg.Parameter):  # Columns that start with @
            return TableColumn(column_name=exp.sql())

        elif isinstance(exp, sg.Literal):
            val = exp.this

            try:
                val = int(val)
            except ValueError:
                pass

            return Constant(value=val)

        else:
            raise SyntaxError(f"Unsupported expression type {type(exp).__name__}: {exp.sql()}")

    @classmethod
    def _parse_bool_expression(cls, *, exp: sg.Expression) -> BooleanExpression:
        if isinstance(exp, sg.EQ):
            return BinaryBooleanExpression(left=cls._parse_term(exp=exp.left), right=cls._parse_term(exp=exp.right), operator=BooleanBinaryOperators.EQ)
        elif isinstance(exp, sg.NEQ):
            return BinaryBooleanExpression(left=cls._parse_term(exp=exp.left), right=cls._parse_term(exp=exp.right), operator=BooleanBinaryOperators.NEQ)
        elif isinstance(exp, sg.GT):
            return BinaryBooleanExpression(left=cls._parse_term(exp=exp.left), right=cls._parse_term(exp=exp.right), operator=BooleanBinaryOperators.GT)
        elif isinstance(exp, sg.GT):
            return BinaryBooleanExpression(left=cls._parse_term(exp=exp.left), right=cls._parse_term(exp=exp.right), operator=BooleanBinaryOperators.LT)
        elif isinstance(exp, sg.And):
            return BinaryBooleanExpression(
                left=cls._parse_bool_expression(exp=exp.left), right=cls._parse_bool_expression(exp=exp.right), operator=BooleanBinaryOperators.AND
            )
        elif isinstance(exp, sg.Or):
            return BinaryBooleanExpression(
                left=cls._parse_bool_expression(exp=exp.left), right=cls._parse_bool_expression(exp=exp.right), operator=BooleanBinaryOperators.OR
            )
        else:
            raise SyntaxError(f"Unsupported boolean expression: {type(exp).__name__}")

    @classmethod
    def _parse_group_by(cls, *, group_by: sg.Group, alias_to_term: typing.Mapping[str, Term]) -> typing.Set[Term]:
        terms = set()

        for exp in group_by.expressions:
            if isinstance(exp, sg.Column):  # i.e table column
                if selected_term := alias_to_term.get(exp.name):
                    terms.add(selected_term)
                else:
                    terms.add(TableColumn(column_name=exp.name))
            elif isinstance(exp, sg.Parameter):  # Columns that starts with @
                if selected_term := alias_to_term.get(exp.sql()):
                    terms.add(selected_term)
                else:
                    terms.add(TableColumn(column_name=exp.sql()))
            else:
                raise SyntaxError(f"Unexpected GROUP BY expression type: {type(exp).__name__}")

        return terms

    @classmethod
    def _parse_order_by(cls, *, order_by: sg.Order, alias_to_term: typing.Mapping[str, Term]) -> OrderBy:
        if len(order_by.expressions) != 1:
            raise SyntaxError(f"Expected one order expression, got: {len(order_by.expressions)}")

        ordered = order_by.expressions[0]

        if not isinstance(ordered, sg.Ordered):
            raise TypeError(f"Unexpected order type: {type(ordered).__name__}")

        exp = ordered.this

        if not isinstance(exp, sg.Column):
            raise SyntaxError(f"Unexpected order expression type: {type(exp).__name__}")

        if selected_term := alias_to_term.get(exp.name):
            order_by_term = selected_term
        else:
            order_by_term = cls._parse_term(exp=exp)

        return OrderBy(term=order_by_term, desc=ordered.args.get("desc") or False)

    @classmethod
    def _parse_limit(cls, *, limit: sg.Limit) -> int:
        exp = limit.expression

        if not isinstance(exp, sg.Literal):
            raise SyntaxError(f"Unexpected limit expression type: {type(exp).__name__}")

        return int(exp.this)
