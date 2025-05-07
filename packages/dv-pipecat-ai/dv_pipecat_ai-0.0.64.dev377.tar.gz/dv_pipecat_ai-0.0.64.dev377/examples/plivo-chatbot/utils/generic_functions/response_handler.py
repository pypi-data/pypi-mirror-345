"""Response formatters for API responses.

This module contains formatter functions that process API responses
before they are returned to the LLM, allowing for custom formatting
and data transformation.
"""

import json
import re
import traceback


import pandas as pd
from loguru import logger
from num_to_words import num_to_word as num2words

# Dictionary to store all registered response formatters
response_formatters = {}


def register_response_formatter(name):
    """Decorator to register a response formatter function."""

    def decorator(func):
        response_formatters[name] = func
        return func

    return decorator


# Example response formatter
@register_response_formatter("practo_slots_formatter")
async def practo_slots_formatter(response_data, args):
    def _num_to_word(num):
        return num2words(num, lang="en")

    """Process order details response."""
    logger.debug(
        f"Processing order details response for doctor: {args.get('doctor_id', 'unknown')}"
    )
    logger.debug(f"Response: {response_data}")

    slots_dict = response_data.get("slots", [])
    amount = response_data.get("amount", "Not Available")
    base_df = pd.DataFrame.from_records(slots_dict)
    base_df_processed_list = []

    for _, base_row in base_df.iterrows():
        slot_info = base_row.get("slots", [])
        slot_info_list = []
        row_dict = dict(base_row)
        row_dict.pop("slots", None)

        for slot_info_item in slot_info:
            slot_info_dict = {}

            for key, value in slot_info_item.items():
                if isinstance(value, list) and value:
                    for key_, value_ in value[0].items():
                        slot_info_dict[f"{key}_{key_}"] = value_
                else:
                    slot_info_dict[key] = value

            slot_info_list.append(slot_info_dict)

        slot_info_df = pd.DataFrame.from_records(slot_info_list)

        for key__, value__ in row_dict.items():
            if not isinstance(value__, list):
                slot_info_df[key__] = value__

        base_df_processed_list.append(slot_info_df)

    base_df_processed_df = pd.concat(base_df_processed_list, ignore_index=True)
    base_df_processed_df = base_df_processed_df.fillna({"banner_text": "", "relDay": ""})
    filtered_df = base_df_processed_df.query("available == True")

    if filtered_df.shape[0] > 0:
        date_filter = sorted(filtered_df.datestamp.unique())[:3]
        filtered_df = filtered_df[filtered_df.datestamp.isin(date_filter)]

        filtered_df["hour"] = (
            filtered_df["ts"]
            .astype("datetime64[ns]")
            .dt.hour.apply(lambda x: x - 12 if x > 12 else x)
            .astype(str)
        )
        filtered_df["hour"] = filtered_df.hour.apply(_num_to_word)

        # filtered_df["minutes"] = filtered_df["ts"].astype("datetime64[ns]").dt.minute.astype(str)
        # filtered_df["minutes"] = filtered_df.minutes.apply(
        #     lambda x: "" if x == "0" else _num_to_word(x)
        # )

        filtered_df["prefix"] = (
            filtered_df["ts"]
            .astype("datetime64[ns]")
            .dt.hour.apply(lambda x: "pm" if x >= 12 else "am")
            .astype(str)
        )
        filtered_df["prefix"] = filtered_df.apply(
            lambda x: ("evening" if x["prefix"] == "pm" else "morning")
            if x["hour"] not in ("one", "two", "three", "twelve")
            else "",
            axis=1,
        )


        filtered_df["available_slot"] = filtered_df["prefix"] + " " + filtered_df["hour"]
        filtered_df.drop(columns=["ts"], inplace=True)
        llm_df = filtered_df[
            ["date", "available_slot", "day", "weekDay", "relDay"]
        ].drop_duplicates()
        llm_df["consultation_fee"] = amount
        logger.debug(llm_df.to_markdown(index=False))
        return llm_df.to_markdown(index=False)
    else:
        return "No slots available"


@register_response_formatter("cred_order_details_formatter")
async def cred_order_details_formatter(data, args):
    logger.debug(f"Processing order details response for cred: {args.get('order_id', 'unknown')}")
    logger.debug(f"Response: {data}")

    def extract_braced_strings_(text: str) -> list[str]:
        return re.findall(r"{(.*?)}", text)

    decision_tree = {
        "success": {
            "within_tat": {
                "context": {
                    "general": "The payment of {amount} towards your {issuer_name} done on {order_date} is completed. We request you to wait until {promise_timestamp} as {issuer_name} may take upto 48 hours to reflect this amount. If not reflecting in next 48 hrs then we will raise it on priority with the card issuing bank",
                    # "due_date": "We always recommend making payments at least 2 days prior to the due date considering some unfortunate delays that could be caused by numerous technical reasons. We therefore request you to make payments at least 2 days prior to avoid credit scores being impacted",
                    # "credit_score": "We understand your concern regarding the impact on your CIBIL score. Please know that credit bureaus typically consider late payments as part of their scoring models. However, the exact impact can vary based on factors like the duration of the delay and your overall credit history. If the payment is only a few days late, it might not be reported to the credit bureaus. Many banks have a grace period before they report late payments, typically 30 days. We recommend contacting your credit card issuer bank directly with proof of payment to discuss any potential impact on your account and request that they consider this situation in their assessment.We are attempting to have your payment settled at the earliest and apologize for the delay. Appreciate your understanding in this regard",
                    "sms_confirmation": "we understand that you are concerned about the payment since you have not received a confirmation SMS from {issuer_name}, note, it can take upto 2 working days to send a confirmation SMS. don't worry bank name will consider the payment success date as {order_date}",
                }
            },
            "outside_tat": {
                "context": {
                    "general": "The payment of {amount} was expected to be settled towards your {issuer_name} card by {promise_timestamp}. we will transfer this call to our support team who will investigate the matter and raise it on priorty with {issuer_name} bank"
                }
            },
        },
        "processing": {
            "within_tat": {
                "context": {
                    "general": "The payment of {amount} expected to be settled towards your {issuer_name} card by {promise_timestamp}. most credit card bill payments made on CRED reflect instantly, since they're made through the RBI-approved Bharat Connect platform but in rare cases can take upto 24 hours",
                    # "due_date": "We always recommend making payments at least 2 days prior to the due date considering some unfortunate delays that could be caused by numerous technical reasons. We therefore request you to make payments at least 2 days prior to avoid credit scores being impacted.",
                    # "credit_score": "We understand your concern regarding the impact on your CIBIL score. Please know that credit bureaus typically consider late payments as part of their scoring models. However, the exact impact can vary based on factors like the duration of the delay and your overall credit history. If the payment is only a few days late, it might not be reported to the credit bureaus. Many banks have a grace period before they report late payments, typically 30 days. We recommend contacting your credit card issuer bank directly with proof of payment to discuss any potential impact on your account and request that they consider this situation in their assessment. We are attempting to have your payment settled at the earliest and apologize for the delay. Appreciate your understanding in this regard",
                }
            },
            "outside_tat": {
                "context": {
                    "general": "The payment of {amount} was expected to be settled towards your {issuer_name} card by {promise_timestamp} but we see its been more than 24 hours. we will transfer this call to our support team who will investigate the matter and raise it on priorty with {issuer_name} bank"
                }
            },
        },
        "failed": {
            "within_tat": {
                "context": {
                    "general": "The payment of {amount} towards your {issuer_name} card has unfortunately failed. Be rest assured we have initiated the refund on {refund_date} and the status of your refund is {refund_status}. The refund will be credited back to your {payment_method} by {refund_timestamp}",
                    # "due_date": "today is my due date We understand and we don't want our members to face such issues. We encourage you to go ahead and make another payment using CRED as most credit card bill payments made on CRED reflect instantly, since they're made through the RBI-approved Bharat Connect platform. Also we have CRED gurantee in place which means as long as you pay on or before due date CRED guarantee ensures you're protected from late fees as per the CRED gurantee policy.",
                    # "credit_score": "We understand your concern regarding the impact on your CIBIL score. Please know that credit bureaus typically consider late payments as part of their scoring models. However, the exact impact can vary based on factors like the duration of the delay and your overall credit history. If the payment is only a few days late, it might not be reported to the credit bureaus. Many banks have a grace period before they report late payments, typically 30 days. We recommend contacting your credit card issuer bank directly with proof of payment to discuss any potential impact on your account and request that they consider this situation in their assessment. We are attempting to have your payment settled at the earliest and apologize for the delay. Appreciate your understanding in this regard",
                }
            },
            "outside_tat": {
                "context": {
                    "general": "The payment of {amount} towards your {issuer_name} card has unforutunately failed. the refund was expected to be credited back to your {payment_method} by {refund_timestamp}. we will transfer this call to our support team who will investigate the matter and raise it on priorty with {issuer_name} bank"
                }
            },
        },
        "cancellation_possible": {
            "true": "We can go ahead and cancel your credit card payment, but please note it may take upto 5 to 7 days for refund. Should we go ahead and intiaite the cancellaiton?. If user says yes We have successfully cancelled your credit card payment of {amount}. You can expect the refund to be credited in the next 7 days. if no Sure, thanks for your patience. Be rest assured we are working to settle this payemnt towards your {issuer_name} card on priority",
            "false": "Unfortunately, this order cannot be cancelled at this time. We reques you to please wait till {promise_timestamp}, and if the payment has still not reached your card then please call us back and we will look into this on priority.",
        },
        "late_fee_eligible": {
            "true": "we understand you have concerns around late fee charges. as seen from our records, there has been a delay for which you have incurred a late fee of {late_fee_amount}. We reques you to please be ready with the latest statement of your {issuer_name} card while we connect you to our support team",
            "false": {
                "completed": "we understand you have concerns around late fee charges. as seen from our records, there has been no delay from our side. incase there are any charges incurred, we would request you to reach out to your bank and get further assistance.",
                "failed": "As per our records the payment of {amount} towards your {issuer_name} card has unfortunately failed/ We encourage you to go ahead and make another payment using CRED as most credit card bill payments made on CRED reflect instantly, since they're made through the RBI-approved Bharat Connect platform. Also we have CRED gurantee in place which means as long as you pay on or before due date CRED guarantee ensures you're protected from late fees as per the CRED gurantee policy.",
                "processing": "As per our records the payment of {amount} towards your {issuer_name} card is still processing. We request you to please wait till {promise_timestamp}, Also we have CRED gurantee in place which means as long as you pay on or before due date CRED guarantee ensures you're protected from late fees as per the CRED gurantee policy.",
            },
        },
    }

    try:
        base_context = decision_tree[data["category"]][data["type"]]["context"]
        late_fee_context = decision_tree["late_fee_eligible"][
            str(data["late_fee_eligible"]).lower()
        ]

        if not isinstance(late_fee_context, str):
            late_fee_context = late_fee_context[data["order_status"].lower()]

        cancellation_possible_context = decision_tree["cancellation_possible"][
            str(data["cancellation_possible"]).lower()
        ]

        for key, item in base_context.items():
            variables = extract_braced_strings_(item)
            if len(variables) != 0:
                variables = {i: data[i] for i in variables}
                item = item.format(**variables)
                base_context[key] = item

        late_fee_variables = {i: data[i] for i in extract_braced_strings_(late_fee_context)}
        cancellation_possible_variable = {
            i: data[i] for i in extract_braced_strings_(cancellation_possible_context)
        }

        late_fee_context = late_fee_context.format(**late_fee_variables)
        cancellation_possible_context = cancellation_possible_context.format(
            **cancellation_possible_variable
        )

        (
            late_fee_context,
            cancellation_possible_context,
        )
        base_context["late_fee"] = late_fee_context
        base_context["cancellation_possible"] = cancellation_possible_context
        for key, value in base_context.items():
            if isinstance(value, str):
                base_context[key] = value.lower()

        base_context.update(dict(data))
        return json.dumps(base_context, indent=2)
    except Exception as e:
        logger.exception(e)
        logger.exception(traceback.format_exc())
        return json.dumps(data, indent=2)