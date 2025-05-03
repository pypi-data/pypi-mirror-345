from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid
from typing import Set, Optional, ClassVar, Dict, Any, List, Union
from pydantic import Field, ConfigDict, computed_field
from ipulse_shared_base_ftredge import Layer, Module, list_as_lower_strings, Subject, SubscriptionPlan, SubscriptionStatus
from ipulse_shared_base_ftredge.enums.enums_iam import IAMUnitType
from .base_data_model import BaseDataModel
# ORIGINAL AUTHOR ="russlan.ramdowar;russlan@ftredge.com"
# CLASS_ORGIN_DATE=datetime(2024, 2, 12, 20, 5)


DEFAULT_SUBSCRIPTION_PLAN = SubscriptionPlan.FREE
DEFAULT_SUBSCRIPTION_STATUS = SubscriptionStatus.ACTIVE

############################################ !!!!! ALWAYS UPDATE SCHEMA VERSION , IF SCHEMA IS BEING MODIFIED !!! ############################################
class Subscription(BaseDataModel):
    """
    Represents a single subscription cycle with enhanced flexibility and tracking.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    VERSION: ClassVar[float] = 2.9  # Incremented version for new fields
    DOMAIN: ClassVar[str] = "_".join(list_as_lower_strings(Layer.PULSE_APP, Module.CORE.name, Subject.SUBSCRIPTION.name))
    OBJ_REF: ClassVar[str] = "subscription"

    # System-managed fields (read-only)
    schema_version: float = Field(
        default=VERSION,
        description="Version of this Class == version of DB Schema",
        frozen=True
    )

    # Unique identifier for this specific subscription instance - now auto-generated
    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this subscription instance"
    )

    # Plan identification
    plan_name: SubscriptionPlan = Field(
        ...,  # Required field, no default
        description="Subscription Plan Name"
    )

    plan_version: int = Field(
        ...,  # Required field, no default
        description="Version of the subscription plan"
    )

    @computed_field
    def plan_id(self) -> str:
        """
        Generate a plan identifier combining plan name and version.
        Format: {plan_name}_{plan_version}
        Example: "free_subscription_1"
        """
        return f"{self.plan_name.value}_{self.plan_version}"

    # Cycle duration fields
    cycle_start_date: datetime = Field(
        ...,  # Required field, no default
        description="Subscription Cycle Start Date"
    )

    # New fields for more flexible cycle management
    validity_time_length: int = Field(
        ...,  # Required field, no default
        description="Length of subscription validity period (e.g., 1, 3, 12)"
    )

    validity_time_unit: str = Field(
        ...,  # Required field, no default
        description="Unit of subscription validity ('minute', 'hour', 'day', 'week', 'month', 'year')"
    )

    # Computed cycle_end_date based on start date and validity
    @computed_field
    def cycle_end_date(self) -> datetime:
        """Calculate the end date based on start date and validity period."""
        if self.validity_time_unit == "minute":
            return self.cycle_start_date + relativedelta(minutes=self.validity_time_length)
        elif self.validity_time_unit == "hour":
            return self.cycle_start_date + relativedelta(hours=self.validity_time_length)
        elif self.validity_time_unit == "day":
            return self.cycle_start_date + relativedelta(days=self.validity_time_length)
        elif self.validity_time_unit == "week":
            return self.cycle_start_date + relativedelta(weeks=self.validity_time_length)
        elif self.validity_time_unit == "year":
            return self.cycle_start_date + relativedelta(years=self.validity_time_length)
        else:  # Default to months
            return self.cycle_start_date + relativedelta(months=self.validity_time_length)

    # Renewal and status fields
    auto_renew: bool = Field(
        ...,  # Required field, no default
        description="Auto-renewal status"
    )

    status: SubscriptionStatus = Field(
        ...,  # Required field, no default
        description="Subscription Status (active, trial, pending_confirmation, etc.)"
    )

    # New fields for enhanced subscription management
    # Update the type definition to use string keys for IAMUnitType
    iam_domain_permissions: Dict[str, Dict[str, List[str]]] = Field(
        ...,  # Required field, no default
        description="IAM domain permissions granted by this subscription (domain -> IAM unit type -> list of unit references)"
    )

    fallback_plan_id: Optional[str] = Field(
        ...,  # Required field (can be None), no default
        description="ID of the plan to fall back to if this subscription expires"
    )

    price_paid_usd: float = Field(
        ...,  # Required field, no default
        description="Amount paid for this subscription in USD"
    )

    payment_ref: Optional[str] = Field(
        default=None,
        description="Reference to payment transaction"
    )

    # New fields moved from metadata to direct attributes
    subscription_based_insight_credits_per_update: int = Field(
        default=0,
        description="Number of insight credits to add on each update"
    )

    subscription_based_insight_credits_update_freq_h: int = Field(
        default=24,
        description="Frequency of insight credits update in hours"
    )

    extra_insight_credits_per_cycle: int = Field(
        default=0,
        description="Additional insight credits granted per subscription cycle"
    )

    voting_credits_per_update: int = Field(
        default=0,
        description="Number of voting credits to add on each update"
    )

    voting_credits_update_freq_h: int = Field(
        default=62,
        description="Frequency of voting credits update in hours"
    )

    # General metadata for extensibility
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the subscription"
    )

    # Methods for subscription management
    def is_active(self) -> bool:
        """Check if the subscription is currently active."""
        now = datetime.now(timezone.utc)
        return (
            self.status == SubscriptionStatus.ACTIVE and
            self.cycle_start_date <= now <= self.cycle_end_date
        )

    def is_expired(self) -> bool:
        """Check if the subscription has expired."""
        now = datetime.now(timezone.utc)
        return now > self.cycle_end_date

    def days_remaining(self) -> int:
        """Calculate the number of days remaining in the subscription."""
        now = datetime.now(timezone.utc)
        if now > self.cycle_end_date:
            return 0
        return (self.cycle_end_date - now).days