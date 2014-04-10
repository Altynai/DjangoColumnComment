#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @auther: Altynai

__version__ = "0.0.2"

from optparse import OptionParser
import os


FIELD_TYPE = {
    "AutoField": "int",
    "BigIntegerField": "bigint",
    "BooleanField": "tinyint",
    "CharField": "varchar",
    "DateField": "date",
    "DateTimeField": "datetime",
    "FloatField": "double",
    "IntegerField": "int",
    "SmallIntegerField": "smallint",
    "TextField": "longtext",
    "ForeignKey": "int",
    "NullBooleanField": "tinyint",
}


def is_django_project(path):
    if not os.path.isdir(path):
        return False
    file_must_exists = ["__init__.py", "manage.py", ]
    file_name_list = os.listdir(path)

    for file_name in file_must_exists:
        if file_name not in file_name_list:
            return False
    else:
        return True


def django_project_name(django_project_path):
    try:
        return django_project_path.split("/")[-1]
    except:
        return ""


def _dump_comment_sql(django_model):
    global FIELD_TYPE
    database_name = django_model._db
    table_name = django_model._meta.db_table
    sqls = list()
    sql_header = "--;\n-- Add column comment for table `%s`;\n--"% table_name
    sqls.append(sql_header)
    for field in django_model._meta.fields:
        column_name = field.db_column if field.db_column else field.attname
        field_type = field.__class__.__name__
        if field_type not in FIELD_TYPE:
            raise KeyError("Unknown Field(%s)" % field_type)
        column_type = FIELD_TYPE[field_type]
        column_comment = field.verbose_name
        if field_type in ("CharField", ):
            column_type = r"%s(%s)" % (column_type, field.max_length)
        column_null = r"DEFAULT NULL" if field.null else r"NOT NULL"
        sqls.append(
            r"ALTER TABLE `%s`.`%s` MODIFY `%s` %s %s COMMENT '%s'" %
            (database_name,
             table_name,
             column_name,
             column_type,
             column_null,
             column_comment))
    return "\n".join(map(lambda x: "%s;" % x, sqls))


def search_module(django_project_path, module_name):
    project_name = django_project_name(django_project_path)
    if not project_name:
        return None
    for relative_path in os.listdir(django_project_path):
        absolute_path = r"%s/%s" % (django_project_path, relative_path)
        if (not os.path.isdir(absolute_path)) or (relative_path.startswith(".")):
            continue
        try:
            module_path = r"%s.%s.%s" % (
                project_name, relative_path, module_name)
            __import__(module_path, fromlist=[relative_path])
            return module_path
            break
        except ValueError as e:
            raise e
        except ImportError as e:
            continue
    else:
        return None


def dump_comment_sql(django_project_path):
    if not is_django_project(django_project_path):
        return ""
    project_name = django_project_name(django_project_path)
    if not project_name:
        return ""

    # 尝试初始化django环境
    module_name = search_module(django_project_path, "settings")
    if not module_name:
        return ""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", module_name)

    # 尝试获得model所在目录
    module_name = search_module(django_project_path, "models")
    if not module_name:
        return ""
    module = __import__(module_name, fromlist=[module_name.split(".")[-2]])

    sqls = list()
    for key in module.__dict__:
        django_model = getattr(module, key)
        if hasattr(django_model, "_meta"):
            sqls.append(_dump_comment_sql(django_model))
    return "\n".join(sqls)


def search_django_project(path, recursion=False):
    path_joiner = lambda x: r"%s/%s" % (path, x)
    absolute_path = map(path_joiner, os.listdir(path))
    # 当前目录下的所有子目录
    current_dirs = filter(is_django_project, absolute_path)
    # 递归子目录
    result = list()
    if recursion:
        for current_dir in current_dirs:
            result += search_django_project(current_dir, recursion)
    # 考虑当前目录
    if is_django_project(path):
        result.append(path)
    return result


if __name__ == '__main__':
    usage = "usage: %prog [options] path"
    cmd_parser = OptionParser(usage=usage)
    cmd_parser.add_option("-r", "--recursion", action="store_true", default=False,
                          help=r"serach for the possible django projects hierarchically")
    cmd_parser.add_option("-o", "--output", default=".", metavar="OUTPUT",
                          help=r"save the the result sql file to the path [default: %default]")
    default_name = r"models-comment.sql"
    cmd_parser.add_option("-n", "--name", default=default_name, metavar="NAME",
                          help=r"save result to the named file [default: %default]")
    options, args = cmd_parser.parse_args()
    if len(args) != 1:
        cmd_parser.error("incorrect number of arguments")
    search_path = os.path.abspath(args[0])
    # 过滤comment语句
    sqls = map(
        dump_comment_sql,
        search_django_project(
            search_path,
            options.recursion))
    # 输出结果
    output_path = os.path.abspath(options.output)
    with open(r"%s/%s" % (output_path, options.name), "w") as fout:
        print >> fout, "\n".join(filter(None, sqls))
