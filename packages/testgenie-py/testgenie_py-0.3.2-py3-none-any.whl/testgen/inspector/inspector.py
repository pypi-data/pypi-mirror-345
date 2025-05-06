from ast import FunctionType
import inspect

class Inspector:

    @staticmethod
    def get_functions(file):
        return inspect.getmembers(file, inspect.isfunction)

    @staticmethod
    def get_signature(func: FunctionType):
        return inspect.signature(func)

    @staticmethod
    def get_code(func: FunctionType):
        return inspect.getsource(func)

    @staticmethod
    def get_params(sig: inspect.Signature):
        return sig.parameters

    @staticmethod
    def get_params_not_self(sig: inspect.Signature):
        params = sig.parameters
        return [param for param, value in params.items() if param != 'self']

    def func_inspect(self, function_name) -> list[tuple]:
        test_cases: list[tuple] = []

        functions = inspect.getmembers(function_name, inspect.isfunction)

        for name, func in functions:
            print(f"Function Name: {name}")
            signature = inspect.signature(func)
            print(f"Signature: {signature}")
            for param in signature.parameters:
                print(f"Param: {param}")
            print(f"Function Code: {inspect.getsource(func)}")

            docstring: str = inspect.getdoc(func)
            print(f"Docstring: {docstring}")

            cases: list[str] = docstring.split(",")

            for case in cases:
                io: list[str] = case.split("-")
                input: str = io[0][7:].strip()
                output: str = io[1][8:].strip()
                print(f"Input: {input}")
                print(f"Output: {output}")
                test_cases.append((name, (input, output)))

        return test_cases


if __name__ == "__main__":
    inspector = Inspector()
    test_cases = inspector.func_inspect()
    print(f"Collected Test Cases: {test_cases}")