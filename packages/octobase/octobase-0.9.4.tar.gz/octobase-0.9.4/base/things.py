#!/opt/local/bin/python

import base


class Thing:
  ''' base class for every (new) thing in our system '''

  def __init__(self, **kwargs):
    base.utils.SetAttrs(self, **kwargs)

  __in_repr         = False
  def __repr__(self):
    if self.__in_repr:
      return ''
    basic           = base.utils.ClassName(self) + '_' + hex(id(self))[-3:]
    self.__in_repr  = True
    stred           = str(self)
    self.__in_repr  = False
    return stred and (basic + "('" + str(self) + "')") or basic

  ###
  ## ATTRIBUTES
  #     very basic ways of thunking this object

  ATTRIBUTES        = None          # meaningful attributes that should be included in Dupe() and Copy()

  @base.utils.anyproperty
  def attributes(zelf):
    ''' returns a list of the names of meaningful attributes on ourself '''
    return zelf.ATTRIBUTES or []

  def Attributes(self, skip=None, skip_nones=False, recurse=True):
    ''' returns a dictionary of our attributes '''
    if skip and isinstance(skip, str):
      skip          = set([skip])
    results         = {x: getattr(self, x) for x in (self.ATTRIBUTES or []) if not skip or not x in skip}
    if skip_nones:
      results       = {x:y for x,y in results.items() if y is not None}
    if recurse:
      for key, val in results.items():
        if isinstance(val, Thing):
          results[key]  = val.Attributes(skip=skip, skip_nones=skip_nones)
    return results

  def Describe(self, **kwargs):
    ''' emits a string with all our attributes and values '''
    attribs         = self.Attributes(**kwargs)
    padding         = sum(len(x) for x in attribs) + 2
    lines           = [base.utils.PadString(x + ': ', padding) + str(y) for x,y in attribs.items()]
    if lines:
      return base.utils.ObjectName(self) + '\n - ' + '\n - '.join(lines)
    else:
      return base.utils.ObjectName(self)

  def Reset(self):
    ''' returns our attrs to a pristine state '''
    base.utils.SetAttrs(self, **{x: None for x in (self.ATTRIBUTES or [])})

  def Dupe(self, **kwargs):
    ''' returns a copy of ourself; applies kwargs '''
    other           = type(self)().Copy(self)
    if kwargs:
      base.utils.SetAttrs(other, **kwargs)
    return other

  def Copy(self, other, nones=True):
    ''' copies any attrs we can from the other into ourself; returns self '''
    attr0           = self.ATTRIBUTES and set(self.ATTRIBUTES) or set()
    attr1           = hasattr(other, 'ATTRIBUTES') and other.ATTRIBUTES and set(other.ATTRIBUTES) or attr0
    attrs           = attr0 & attr1
    if not attrs:
      raise base.errors.NoAttributes(self, other)
    for attr in (attr0 & attr1):
      val           = getattr(other, attr)
      if nones or val is not None:
        setattr(self, attr, val)
    return self

  def AppName(self):
    return base.utils.AppName(self)

  def ClassName(self):
    return base.utils.ClassName(self)
