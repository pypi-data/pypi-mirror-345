def Return_Value_Of(Value):
  return Value

def Crash():
  Crash()

def Range(Number):
  return range(Number)

def Len(List):
  return len(List)

def Int(Number):
  return int(Number)

def String(Message):
  return str(Message)

def Bool(Boolean):
  return bool(Boolean)

def Float(Decimal):
  return float(Decimal)

def List(Array):
  return list(Array)

def Print(Message):
  print(Message)

def Print_Multiple_Times(Count, Msg):
  For_Loop(Range(Count), lambda Message: Print(Message), Msg)

def Sum_Multiple_Numbers(*Numbers):
  Total = 0
  for Number in Numbers: Total += Number
  return Total

def Multiply_Multiple_Numbers(*Numbers):
  Total = 1
  for Number in Numbers: Total *= Number
  return Total

def For_Loop(List, Code, PassElement, *Arguments):
  for Element in List:
    if PassElement: Code(Element, *Arguments)
    else: Code(*Arguments)

def Get_Input_From_User(Message, Type = String):
  return Return_Value_Of(Type(input(Message)))