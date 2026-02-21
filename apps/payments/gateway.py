"""
Mock Cielo payment gateway integration.

In production, this module communicates with Cielo's API (api.cieloecommerce.cielo.com.br).
For this demo, all responses are simulated with realistic data structures.
"""
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CieloResponse:
    success: bool
    transaction_id: str
    authorization_code: str
    message: str


class CieloGateway:
    """Mock implementation of Cielo 3.0 payment gateway."""

    DEMO_PREFIX = "CIELO-DEMO"

    def authorize(self, order_id: int, amount: float, card_number: str, **kwargs) -> CieloResponse:
        """
        Simulate a Cielo payment authorization.

        In production, this sends a POST to:
        https://apisandbox.cieloecommerce.cielo.com.br/1/sales/

        Returns a mock authorization response.
        """
        transaction_id = f"{self.DEMO_PREFIX}-{uuid.uuid4().hex[:12].upper()}"
        authorization_code = f"AUTH-{datetime.now().strftime('%H%M%S')}"

        if card_number.endswith("0000"):
            return CieloResponse(
                success=False,
                transaction_id=transaction_id,
                authorization_code="",
                message="Transação não autorizada — cartão de teste negado",
            )

        return CieloResponse(
            success=True,
            transaction_id=transaction_id,
            authorization_code=authorization_code,
            message="Transação autorizada com sucesso",
        )

    def capture(self, transaction_id: str) -> CieloResponse:
        """
        Simulate a Cielo payment capture.

        In production, this sends a PUT to:
        https://apisandbox.cieloecommerce.cielo.com.br/1/sales/{PaymentId}/capture
        """
        if not transaction_id.startswith(self.DEMO_PREFIX):
            return CieloResponse(
                success=False,
                transaction_id=transaction_id,
                authorization_code="",
                message="Transação não encontrada",
            )

        return CieloResponse(
            success=True,
            transaction_id=transaction_id,
            authorization_code=f"CAP-{datetime.now().strftime('%H%M%S')}",
            message="Pagamento capturado com sucesso",
        )


cielo_gateway = CieloGateway()
