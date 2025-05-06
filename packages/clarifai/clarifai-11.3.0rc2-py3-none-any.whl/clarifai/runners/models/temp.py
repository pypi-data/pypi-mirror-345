prediction = model.predict(text1 = "what is api?")


print(f"The answer is {prediction.answer_text}")


print(f"The answer is {prediction}")




# case 1
class MyModel(ModelClass):

    def predict(self, text: str) -> Output:

        return Output(answer_text= f" {text} hello world")


# case 2
class MyModel(ModelClass):

    def predict(self, text: str) -> str:

        return f" {text} hello world"