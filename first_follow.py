class Grammar:
    def __init__(self):
        self.productions = {}  # Diccionario con las producciones
        self.terminals = set()  # Conjunto de terminales
        self.non_terminals = set()  # Conjunto de no terminales
        self.start_symbol = None  # Símbolo inicial
        self.first = {}  # Diccionario para almacenar FIRST
        self.follow = {}  # Diccionario para almacenar FOLLOW
        self.first_strings = []  # Lista de cadenas para calcular FIRST

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                lines = [
                    line.strip()
                    for line in file
                    if line.strip() and not line.startswith("#")
                ]

                self.start_symbol = lines[0]
                self.non_terminals.add(self.start_symbol)

                for line in lines[1:]:
                    if line.startswith("FIRST:"):
                        cadena = line.split(":", 1)[1].strip()
                        self.first_strings.append(cadena)
                    elif "->" in line:
                        left, right = line.split("->", 1)
                        left = left.strip()
                        self.non_terminals.add(left)

                        productions = [p.strip() for p in right.split("|")]

                        for prod in productions:
                            self.add_production(left, prod)
                    else:
                        print(f"Ignorando línea con formato incorrecto: {line}")

                print(f"Gramática cargada con éxito desde {filename}")
                print(f"Símbolo inicial: {self.start_symbol}")
                print(f"No terminales: {self.non_terminals}")
                print(f"Terminales: {self.terminals}")
                print("Producciones:")
                for nt, prods in self.productions.items():
                    print(f"  {nt} -> {' | '.join(prods)}")

                if self.first_strings:
                    print(f"Cadenas para calcular FIRST: {self.first_strings}")

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {filename}")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")

    def add_production(self, non_terminal, production):
        if non_terminal not in self.productions:
            self.productions[non_terminal] = []
        self.productions[non_terminal].append(production)

        for char in production:
            if char.isupper():
                self.non_terminals.add(char)
            elif char.islower() and char != "e":
                self.terminals.add(char)

    def compute_first(self):
        for nt in self.non_terminals:
            self.first[nt] = set()
        for t in self.terminals:
            self.first[t] = {t}

        if "e" in self.terminals:
            self.first["e"] = {"e"}
        else:
            self.first["e"] = {"e"}

        changed = True
        while changed:
            changed = False

            for nt in self.non_terminals:
                for production in self.productions[nt]:
                    if production == "e":
                        if "e" not in self.first[nt]:
                            self.first[nt].add("e")
                            changed = True
                        continue

                    all_derive_epsilon = True
                    for i, symbol in enumerate(production):
                        if symbol not in self.first:
                            self.first[symbol] = {symbol}

                        before = len(self.first[nt])
                        self.first[nt].update(self.first[symbol] - {"e"})
                        if len(self.first[nt]) > before:
                            changed = True

                        if "e" not in self.first[symbol]:
                            all_derive_epsilon = False
                            break

                    if all_derive_epsilon and "e" not in self.first[nt]:
                        self.first[nt].add("e")
                        changed = True

        return self.first

    def compute_first_of_string(self, string):
        if not string:
            return {"e"}

        first_set = set()

        all_can_derive_epsilon = True

        for symbol in string:
            if symbol not in self.first:
                if symbol.islower() or symbol in self.terminals:
                    first_set.add(symbol)
                else:
                    print(
                        f"Advertencia: El símbolo '{symbol}' no tiene conjunto FIRST calculado"
                    )
                all_can_derive_epsilon = False
                break

            for terminal in self.first[symbol]:
                if terminal != "e":
                    first_set.add(terminal)

            if "e" not in self.first[symbol]:
                all_can_derive_epsilon = False
                break

        if all_can_derive_epsilon:
            first_set.add("e")

        return first_set

    def compute_follow(self):
        for nt in self.non_terminals:
            self.follow[nt] = set()

        self.follow[self.start_symbol] = {"$"}

        changed = True
        while changed:
            changed = False

            for nt in self.non_terminals:
                for production_nt in self.non_terminals:
                    for production in self.productions.get(production_nt, []):
                        if production == "e":
                            continue

                        for i, symbol in enumerate(production):
                            if symbol not in self.non_terminals or symbol != nt:
                                continue

                            rest_of_string = (
                                production[i + 1 :] if i + 1 < len(production) else ""
                            )
                            if not rest_of_string:
                                for terminal in self.follow[production_nt]:
                                    if terminal not in self.follow[symbol]:
                                        self.follow[symbol].add(terminal)
                                        changed = True
                            else:
                                first_of_rest = self.compute_first_of_string(
                                    rest_of_string
                                )

                                for terminal in first_of_rest:
                                    if (
                                        terminal != "e"
                                        and terminal not in self.follow[symbol]
                                    ):
                                        self.follow[symbol].add(terminal)
                                        changed = True

                                if "e" in first_of_rest:
                                    for terminal in self.follow[production_nt]:
                                        if terminal not in self.follow[symbol]:
                                            self.follow[symbol].add(terminal)
                                            changed = True

        return self.follow


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        grammar_file = sys.argv[1]
    else:
        grammar_file = "grammar.txt"

    grammar = Grammar()
    grammar.load_from_file(grammar_file)

    first = grammar.compute_first()

    follow = grammar.compute_follow()

    print("\nRESULTADOS:")
    print("FIRST para símbolos no terminales:")
    for symbol, terminals in first.items():
        if symbol in grammar.non_terminals:
            print(f"FIRST({symbol}) = {terminals}")

    print("\nFOLLOW para no terminales:")
    for nt, terminals in follow.items():
        print(f"FOLLOW({nt}) = {terminals}")

    if grammar.first_strings:
        print("\nFIRST para cadenas específicas:")
        for cadena in grammar.first_strings:
            first_cadena = grammar.compute_first_of_string(cadena)
            print(f"FIRST({cadena}) = {first_cadena}")
