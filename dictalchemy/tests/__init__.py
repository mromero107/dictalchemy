# vim: set fileencoding=utf-8 :
from __future__ import absolute_import, division

from dictalchemy import DictableModel
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.collections import attribute_mapped_collection


# Setup sqlalchemy
engine = create_engine('sqlite:///:memory:', echo=False)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(engine, cls=DictableModel)


class TestCase(unittest.TestCase):

    def setUp(self):
        """ Recreate the database """
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        Base.metadata.drop_all()


class Named(Base):
    __tablename__ = 'named'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name


class NamedWithOtherPk(Base):
    __tablename__ = 'namedwithotherpk'
    id = Column('other_id', Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name


class NamedOtherColumnName(Base):
    __tablename__ = 'named_with_other_column'

    id = Column(Integer, primary_key=True)
    name = Column('namecolumn', String)

    def __init__(self, name):
        self.name = name


class NamedWithSynonym(Base):
    __tablename__ = 'named_with_synonym'

    id = Column(Integer, primary_key=True)
    _name = Column(String)

    def _setname(self, name):
        self._name = name

    def _getname(self):
        return self._name

    name = synonym('_name', descriptor=property(_getname, _setname))

    def __init__(self, name):
        self.name = name


class OneToManyChild(Base):

    __tablename__ = 'onetomanychild'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name


class OneToManyParent(Base):

    __tablename__ = 'onetomanyparent'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    _child_id = Column(Integer, ForeignKey(OneToManyChild.id))

    child = relationship(OneToManyChild,
                         primaryjoin=_child_id == OneToManyChild.id,
                         backref=backref('parent'))

    def __init__(self, name):
        self.name = name


m2m_table = Table('m2m_table',
                  Base.metadata,
                  Column('left_id', Integer,
                         ForeignKey('m2mleft.id'),
                         primary_key=True),
                  Column('right_id', Integer,
                         ForeignKey('m2mright.id'),
                         primary_key=True),
                  )


class M2mLeft(Base):
    __tablename__ = 'm2mleft'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name

    rights = relationship('M2mRight',
                          secondary=m2m_table,
                          backref=backref('lefts'))


class M2mRight(Base):
    __tablename__ = 'm2mright'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name


class MultipleChildChild1Child(Base):

    __tablename__ = 'multiplechildchild1child'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name


class MultipleChildChild1(Base):

    __tablename__ = 'multiplechildchild1'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    _child_id = Column(Integer, ForeignKey(MultipleChildChild1Child.id))

    child = relationship(MultipleChildChild1Child,
                         primaryjoin=_child_id == MultipleChildChild1Child.id,
                         backref=backref('parent'))

    def __init__(self, name):
        self.name = name


class MultipleChildChild2(Base):

    __tablename__ = 'multiplechildchild2'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name


class MultipleChildParent(Base):

    __tablename__ = 'multiplechildparent'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    _child1_id = Column(Integer, ForeignKey(MultipleChildChild1.id))

    _child2_id = Column(Integer, ForeignKey(MultipleChildChild2.id))

    child1 = relationship(MultipleChildChild1,
                          primaryjoin=_child1_id == MultipleChildChild1.id,
                          backref=backref('parent'))

    child2 = relationship(MultipleChildChild2,
                          primaryjoin=_child2_id == MultipleChildChild2.id,
                          backref=backref('parent'))

    def __init__(self, name):
        self.name = name


class WithHybrid(Base):

    __tablename__ = 'withhybrid'

    _id = Column('id', Integer, primary_key=True)

    @hybrid_property
    def id(self):
        return self._id

    @id.setter
    def set_id(self, value):
        self._id = value

    def __init__(self, id):
        self.id = id


class WithDefaultInclude(Base):

    __tablename__ = 'withdefaultinclude'

    dictalchemy_include = ['id_alias']

    id = Column('id', Integer, primary_key=True)

    @hybrid_property
    def id_alias(self):
        return self.id

    @id_alias.setter
    def set_id_alias(self, value):
        self.id = value

    def __init__(self, id):
        self.id = id


class WithAttributeMappedCollectionChild(Base):

    __tablename__ = 'withattributemappedcollectionchild'

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)

    parent_id = Column(Integer, ForeignKey('withattributemappedcollection.id'))

    def __init__(self, name):
        self.name = name


class WithAttributeMappedCollection(Base):

    __tablename__ = 'withattributemappedcollection'

    id = Column(Integer, primary_key=True)

    childs = relationship(WithAttributeMappedCollectionChild,
                          collection_class=attribute_mapped_collection('name'),
                          cascade="all, delete-orphan",
                          backref=backref('parents'))
