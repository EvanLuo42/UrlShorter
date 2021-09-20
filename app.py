import json
import re
import hashlib

from flask import Flask, redirect, request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///url.db', echo=True, connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Url(Base):
    __tablename__ = 'urls'

    id = Column(String(50), primary_key=True, unique=True)
    url = Column(String(100), unique=True)

    def __init__(self, url, id):
        self.url = url
        self.id = id


def url_dump(url_class):
    return {
        'id': url_class.id,
        'url': url_class.url
    }


Base.metadata.create_all(engine, checkfirst=True)


@app.route('/urls')
def get_urls():
    return json.dumps(session.query(Url).all(), default=url_dump)


@app.route('/<site_id>')
def go_url(site_id):
    goal_url = session.query(Url).filter_by(id=site_id).one()
    if goal_url is not None:
        return redirect(goal_url.url)


@app.route('/url')
def add_url():
    if request.args.get('url') is not None:
        if re.match('[a-zA-z]+://[^\s]*', request.args.get('url')) is not None:
            url_entity = Url(url=request.args.get('url'), id=(hashlib.md5(request.args.get('url').encode(encoding='utf-8')).hexdigest())[8:-8].lower())
            session.add(url_entity)
            try:
                session.commit()
            except:
                session.rollback()
            return json.dumps(url_entity, default=url_dump)
        else:
            return {
                'success': 'false'
            }


if __name__ == '__main__':
    app.run()
