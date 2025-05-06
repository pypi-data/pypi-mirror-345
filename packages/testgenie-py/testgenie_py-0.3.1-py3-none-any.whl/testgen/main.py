from testgen.service.service import Service
from testgen.controller.cli_controller import CLIController
from testgen.generator.unit_test_generator import UnitTestGenerator
from testgen.presentation.cli_view import CLIView

def main():
    service = Service()
    view = CLIView()
    controller = CLIController(service, view)
    controller.run()

if __name__ == '__main__':
    main()