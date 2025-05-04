def Return_Value_Of(Value):
  return Value

def Range(Number):
  return range(Number)

def Len(List):
  return len(List)

def For_Loop(List, Code, Argument):
  for Element in List:
    Code(Argument)

def Sum_Three_Numbers(Number_One, Number_Two, Number_Three):
  return Return_Value_Of(Number_One + Number_Two + Number_Three)

def Get_Int_Input_From_User(Message):
  return Return_Value_Of(int(input(Message)))

def Print(Message):
  print(Message)

def Draw_In_The_Chat(Count, Argument):
  For_Loop(Range(Count), lambda Message: Print(Message), Argument)