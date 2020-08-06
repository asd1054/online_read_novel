from flask import Flask,render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:wukong@localhost/online_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭自动跟踪修改
app.secret_key = 'this is a key'

db = SQLAlchemy(app)


class Author(db.Model):
    """数据库的作者表单"""
    __tablename__ = 'author'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(16),unique=True)

    # 关系引用
    books = db.relationship('Book',backref='author')

    def __repr__(self):
        return "<Author: ID->%s\tNAME->%s>"%(self.id,self.name)

class Book(db.Model):
    """数据库的书籍表单"""
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    author_id = db.Column(db.Integer,db.ForeignKey('author.id'))

    def __repr__(self):
        return "<Author: ID->%s\tNAME->%s>" % (self.id, self.name)

class AuthorForm(FlaskForm):
    """网页填写的info表单"""
    author = StringField("作者：",validators=[DataRequired()])
    book = StringField("书籍：",validators=[DataRequired()])
    submit = SubmitField('提交信息')

@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    """删除作者"""
    author = Author.query.get(author_id)

    if author:
        try:
            Book.query.filter_by(author_id=author.id).delete()

            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash("删除作者失败")
            db.session.rollback()
    else:
        flash('作者已删除，请勿反复删除')
    return redirect(url_for('index'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    """删除书籍"""
    book = Book.query.get(book_id)

    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
    else:
        flash('书籍没有找到，无法删除')

    return redirect(url_for('index'))


@app.route('/',methods=['GET','POST'])
def index():
    """程序首页"""
    author_form = AuthorForm()

    if author_form.validate_on_submit():
        author_name = author_form.author.data
        book_name = author_form.book.data

        author = Author.query.filter_by(name=author_name).first()
        if author:
            book = Book.query.filter_by(name=book_name).first()

            if book:
                flash('已存在同名书籍，请勿反复添加')
            else:
                try:
                    new_book = Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash("添加书籍失败，请重试")
    authors = Author.query.all()
    return render_template('books.html',authors = authors,form=author_form)


if __name__ == '__main__':
    app.run()
