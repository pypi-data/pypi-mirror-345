class Calculadora:
    """
    Uma calculadora simples que realiza operações básicas de matemática.
    """

    def soma(self, a, b):
        """
        Soma dois números.

        Args:
            a: Primeiro número
            b: Segundo número

        Returns:
            A soma de a e b
        """
        return a + b

    def subtracao(self, a, b):
        """
        Subtrai b de a.

        Args:
            a: Primeiro número
            b: Segundo número

        Returns:
            A diferença entre a e b
        """
        return a - b

    def multiplicacao(self, a, b):
        """
        Multiplica dois números.

        Args:
            a: Primeiro número
            b: Segundo número

        Returns:
            O produto de a e b
        """
        return a * b

    def divisao(self, a, b):
        """
        Divide a por b.

        Args:
            a: Dividendo
            b: Divisor

        Returns:
            O quociente da divisão de a por b

        Raises:
            ZeroDivisionError: Se b for zero
        """
        if b == 0:
            raise ZeroDivisionError('Não é possível dividir por zero')
        return a / b
