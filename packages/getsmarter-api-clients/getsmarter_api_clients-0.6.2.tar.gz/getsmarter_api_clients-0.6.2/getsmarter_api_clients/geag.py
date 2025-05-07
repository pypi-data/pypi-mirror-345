"""
Client for GetSmarter API Gateway.
"""
import logging

from requests.exceptions import HTTPError

from getsmarter_api_clients.oauth import OAuthApiClient

logger = logging.getLogger(__name__)


class GetSmarterEnterpriseApiClient(OAuthApiClient):
    """
    Client to interface with the GetSmarter Enterprise API Gateway (GEAG).

    For full documentation, visit https://www.getsmarter.com/api-docs.
    """

    def get_terms_and_policies(self):
        """
        Fetch and return the terms and policies from GEAG.

        Returns:
            Dict containing the keys 'privacyPolicy', 'websiteTermsOfUse',
            'studentTermsAndConditions', and 'cookiePolicy'.
        """
        url = f'{self.api_url}/terms'
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def create_allocation(
        self,
        payment_reference,
        address_line1,
        city,
        postal_code,
        country,
        country_code,
        first_name,
        last_name,
        email,
        date_of_birth,
        terms_accepted_at,
        currency,
        order_items,
        address_line2=None,
        state=None,
        state_code=None,
        mobile_phone=None,
        work_experience=None,
        education_highest_level=None
    ):
        """
        Create an allocation (enrollment) through GEAG.

        :Parameters:
          - `payment_reference (str)`: Reference used by enterprise partner
            when payment is made to GetSmarter
          - `address_line1 (str)`: Address Line 1
          - `city (str)`: City
          - `postal_code (str)`: Postal code
          - `country (str)`: Country
          - `country_code (str)`: Country code
          - `first_name (str)`: First name
          - `last_name (str)`: Last name
          - `email (str)`: Email
          - `date_of_birth (str)`: Date of birth
          - `terms_accepted_at (str)`: ISO 8601 timestamp of
            when the terms and policies were accepted
          - `currency (str)`: One of ['USD', 'GBP', 'ZAR', 'EUR', 'AED',
            'SGD', 'HKD', 'SAR', 'INR', 'CAD']
          - `order_items (list of dict)`: Items ordered
          - `address_line2 (str)`: Adress Line 2
          - `state (str)`: State
          - `state_code (str)`: State code
          - `mobile_phone (str)`: Mobile phone number
          - `work_experience (str)`: One of ['None', '1 to 5 years',
            '5 to 15 years', 'More than 15 years']
          - `education_highest_level (str)`: One of ['High school',
            'Bachelor’s degree', 'Master’s degree', 'Doctoral degree',
            'Other tertiary qualification', 'Honours degree',
            'Bachelors degree']

        **Example payload**
          { "paymentReference": "GS-12304",
            'addressLine1': "10 Lovely Street",
            'city': AnyTown,
            'postalCode': 35025,
            'country': "South Africa",
            'countryCode': "ZA"',
            "firstName": "Jan",
            "lastName": "Pan",
            "email": "janpan@gs.com",
            "dateOfBirth": "2021-05-12",
            "termsAcceptedAt": "2021-05-21T17:32:28Z",
            "currency": "ZAR",
            "orderItems": [{ "productId": "product_id", "quantity": 1,
            "normalPrice": 1000, "discount": 500, "finalPrice": 500 }],
            "addressLine1": "Oak Glen",
            "city": "Cape Town",
            "postalCode": "7570",
            "country": "South Africa",
            "countryCode": "ZA" }

        """
        url = f'{self.api_url}/allocations'

        payload = {
            'paymentReference': payment_reference,
            'addressLine1': address_line1,
            'city': city,
            'postalCode': postal_code,
            'country': country,
            'countryCode': country_code,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'dateOfBirth': date_of_birth,
            'termsAcceptedAt': terms_accepted_at,
            'currency': currency,
            'orderItems': order_items,
            # optional fields
            'addressLine2': address_line2,
            'state': state,
            'stateCode': state_code,
            'mobilePhone': mobile_phone,
            'workExperience': work_experience,
            'educationHighestLevel': education_highest_level,
        }
        # remove keys with empty values
        payload = {k: v for k, v in payload.items() if v is not None}

        # log the payload
        payload_message = (
            f'Attempting allocation for order {payment_reference} '
            f'with payload: {payload}'
        )
        logger.info(payload_message)

        # send the allocation
        response = self.post(url, json=payload)
        try:
            response.raise_for_status()
        except HTTPError:
            message = (
              f'Allocation failed to be created for order {payment_reference} '
              f'with reasons: {response.text}, '
              f'with payload: {payload}'
            )
            logger.error(message)
            raise
        return response

    # This is for the endpoint created by GetSmarter for enterprise
    # specific needs. The fields with a default of None are optional
    # fields. Notice this endpoint differs in the amount of optional
    # fields when compared against the other allocation endpoint.
    def create_enterprise_allocation(
        self,
        payment_reference,
        enterprise_customer_uuid,
        first_name,
        last_name,
        email,
        date_of_birth,
        terms_accepted_at,
        data_share_consent,
        currency,
        order_items,
        address_line1=None,
        address_line2=None,
        city=None,
        postal_code=None,
        state=None,
        state_code=None,
        country=None,
        country_code=None,
        mobile_phone=None,
        work_experience=None,
        education_highest_level=None,
        org_id=None,
        should_raise=True,
    ):
        """
        Create an enterprise_allocation (enrollment) through GEAG.

        :Parameters:
          - `payment_reference (str)`: Reference used by enterprise partner
            when payment is made to GetSmarter
          - `enterprise_customer_uuid (str)`: A uuid used by enterprise partner
             to identify which enterprise customer the order was placed for
          - `first_name (str)`: First name
          - `last_name (str)`: Last name
          - `email (str)`: Email
          - `date_of_birth (str)`: Date of birth
          - `terms_accepted_at (str)`: ISO 8601 timestamp of
            when the terms and policies were accepted
          - `data_share_consent (bool)`: Learner consent for data sharing
          - `currency (str)`: One of ['USD', 'GBP', 'ZAR', 'EUR', 'AED',
            'SGD', 'HKD', 'SAR', 'INR', 'CAD']
          - `order_items (list of dict)`: Items ordered
          - `address_line1 (str)`: Address Line 1
          - `address_line2 (str)`: Adress Line 2
          - `city (str)`: City
          - `postal_code (str)`: Postal code
          - `state (str)`: State
          - `state_code (str)`: State code
          - `country (str)`: Country
          - `country_code (str)`: Country code
          - `mobile_phone (str)`: Mobile phone number
          - `work_experience (str)`: One of ['None', '1 to 5 years',
            '5 to 15 years', 'More than 15 years']
          - `education_highest_level (str)`: One of ['High school',
            'Bachelor’s degree', 'Master’s degree', 'Doctoral degree',
            'Other tertiary qualification', 'Honours degree',
            'Bachelors degree']
          - `org_id (str)`: `auth_org_id` from the learner’s
            `EnterpriseCustomer` record

        **Example payload**
          { "paymentReference": "GS-12304",
            "enterpriseCustomerUuid": "69C3E666-4740-4531-9435-A3EDF6D28C01",
            "firstName": "Jan",
            "lastName": "Pan",
            "email": "janpan@gs.com",
            "dateOfBirth": "2021-05-12",
            "termsAcceptedAt": "2021-05-21T17:32:28Z",
            "currency": "ZAR",
            "orderItems": [{ "productId": "product_id", "quantity": 1,
            "normalPrice": 1000, "discount": 500, "finalPrice": 500 }],
            "addressLine1": "Oak Glen",
            "city": "Cape Town",
            "postalCode": "7570",
            "country": "South Africa",
            "countryCode": "ZA",
            "orgId": "12KJ2j9js0" }

        """
        url = f'{self.api_url}/enterprise_allocations'

        payload = {
            'paymentReference': payment_reference,
            'enterpriseCustomerUuid': enterprise_customer_uuid,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'dateOfBirth': date_of_birth,
            'termsAcceptedAt': terms_accepted_at,
            'dataShareConsent': data_share_consent,
            'currency': currency,
            'orderItems': order_items,
            # optional fields
            'addressLine1': address_line1,
            'addressLine2': address_line2,
            'city': city,
            'postalCode': postal_code,
            'state': state,
            'stateCode': state_code,
            'country': country,
            'countryCode': country_code,
            'mobilePhone': mobile_phone,
            'workExperience': work_experience,
            'educationHighestLevel': education_highest_level,
            'orgId': org_id,
        }
        # remove keys with empty values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = self.post(url, json=payload)
        try:
            response.raise_for_status()
        except HTTPError:
            message = (
              f'Enterprise allocation failed to be created for order {payment_reference} '
              f'with reasons: {response.text}, '
              f'with payload: {payload}'
            )
            logger.error(message)
            if should_raise:
                raise
        return response

    def cancel_enterprise_allocation(
        self,
        order_uuid,
        should_raise=True,
    ):
        """
        Cancel an enterprise_allocation (enrollment) through GEAG.

        :Parameters:
          - `order_uuid` (str): The order UUID of the allocation
          - `should_raise` (boolean): Should exceptions be re-raised
        """
        url = f'{self.api_url}/enterprise_allocations/cancel'

        payload = {
            'orderUuid': str(order_uuid),
        }

        response = self.post(url, json=payload)
        try:
            response.raise_for_status()
        except HTTPError:
            message = (
              f'Allocation cancelation failed for {order_uuid} '
              f'with reasons: {response.text}, '
              f'with payload: {payload}'
            )
            logger.error(message)
            if should_raise:
                raise
        return response
