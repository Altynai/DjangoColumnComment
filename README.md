django-column-cmment
====================

convert django model's verbose_name to a modified sql


Example
====================

you have a table named `table` as below

```python

class Book(Model):
    ISBN = CharField(max_length=32, null=False, default="", db_column="ISBN", verbose_name=r"book ISBN")
    name = CharField(max_length=32, null=True, db_column="name", verbose_name=r"book name")
    price = FloatField(null=False, default=0, db_column="price", verbose_name=r"book price")
    create_time = DateTimeField(auto_now_add=True, db_column="create_time", verbose_name=r"book created time")

    _db = "black_book_shop"

    class Meta:
        db_table = "book"
```

it will dumps serveral lines of sql as below

```sql
ALTER TABLE `black_book_shop`.`book` MODIFY `id` int NOT NULL COMMENT 'ID';
ALTER TABLE `black_book_shop`.`book` MODIFY `ISBN` varchar(32) NOT NULL COMMENT 'book ISBN';
ALTER TABLE `black_book_shop`.`book` MODIFY `name` varchar(32) DEFAULT NULL COMMENT 'book name';
ALTER TABLE `black_book_shop`.`book` MODIFY `price` double NOT NULL COMMENT 'book price';
ALTER TABLE `black_book_shop`.`book` MODIFY `create_time` datetime NOT NULL COMMENT 'book created time'
```

Installation
====================

```bash
git clone git@github.com:Altynai/django-column-comment.git --depth=1
cd django-column-comment
python setup.py install

```


Usage
====================

```python

Usage: dcc.py [options] path

Options:
  -h, --help            show this help message and exit
  -r, --recursion       serach for the possible django projects hierarchically
  -o OUTPUT, --output=OUTPUT
                        save the the result sql file to the path [default: .]
  -n NAME, --name=NAME  save result to the named file [default: models-comment.sql]
```
