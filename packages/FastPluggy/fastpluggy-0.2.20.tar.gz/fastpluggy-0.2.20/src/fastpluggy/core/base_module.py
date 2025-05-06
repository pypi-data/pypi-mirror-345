import ast
import os

from loguru import logger


class BaseModule:
    def discover_models(self, base_class_name="Base"):
        """
        Discover SQLAlchemy models in a plugin's models.py file using AST.

        Args:
            base_class_name (str): Name of the SQLAlchemy base class (default is 'Base').
        """
        try:
            # Construct the path to models.py
            models_path = os.path.join(self.path, "models.py")
            if not os.path.exists(models_path):
                logger.debug(f"No models.py file found in module '{self.name}'.")
                return

            # Parse the models.py file using AST
            with open(models_path, "r") as file:
                tree = ast.parse(file.read())

            for node in ast.walk(tree):
                # Look for class definitions
                if isinstance(node, ast.ClassDef):
                    # Check if the class inherits from the specified base class
                    for base in node.bases:
                        if (
                                isinstance(base, ast.Name) and base.id == base_class_name
                        ) or (
                                isinstance(base, ast.Attribute) and base.attr == base_class_name
                        ):
                            # Check for __tablename__ attribute
                            tablename = None
                            for body_item in node.body:
                                if isinstance(body_item, ast.Assign):
                                    for target in body_item.targets:
                                        if (
                                                isinstance(target, ast.Name)
                                                and target.id == "__tablename__"
                                        ):
                                            if isinstance(body_item.value, ast.Constant):
                                                tablename = body_item.value.value

                            # Add the discovered model to the module's models
                            self.models.append(
                                {"class_name": node.name, "table_name": tablename,
                                 "module_name": '.'.join([self.package_name, 'models'])}
                            )
                            logger.info(
                                f"Discovered model '{node.name}' with table '{tablename}' in module '{self.name}'"
                            )

            if not self.models:
                logger.debug(f"No SQLAlchemy models discovered in module '{self.name}'.")
        except Exception as e:
            logger.error(f"Error discovering models in module '{self.name}': {e}")
