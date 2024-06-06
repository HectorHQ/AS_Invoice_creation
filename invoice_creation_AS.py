import pandas as pd
import streamlit as st
import json
import requests
from accounting_service_payments_applications import get_bearer_token,create_headers


st.set_page_config('Invoice Creation Automation Service',
                    page_icon= ':file_folder:',
                    layout= 'wide'
                    )

st.title(':orange[Invoice Creation] Automation Service :file_folder:')


@st.cache_data
def load_dataframe(file):
    """
    Loads the uploaded file into a Pandas DataFrame.
    """

    file_extension = file.name.split(".")[-1]
    
    if file_extension == "csv":
        df = pd.read_csv(file)

    elif file_extension == "xlsx":
        df = pd.read_excel(file)

    return df


def invoice_creation_AS(headers,org_id,date,amount,toogle,notes,invoice_id):
    
    json_data = {
        'operationName': 'postAccountingAPICreateManualInvoiceForOrg',
        'variables': {
            'input': {
                'invoiceTypeGroupType': 'FEE',
                'invoiceTypeId': invoice_id,
                'paidBy': org_id,
                'paidTo': 'TWluaW1hbE9yZ2FuaXphdGlvbkJhbmtpbmc6OTYwZjRiNTYtYzVkYi00MWQ2LTgyNGQtODU2M2U5OGQ4NTBl',
                'dueDate': date +'T06:00:00.000Z',
                'amount': amount,
                'enforcedDeductible': toogle,
                'adminNotes': notes,
            },
        },
        'query': 'mutation postAccountingAPICreateManualInvoiceForOrg($input: PostAccountingAPICreateManualInvoiceForOrgInput!) {\n  postAccountingAPICreateManualInvoiceForOrg(input: $input)\n}\n',
    }

    response = requests.post('https://api.nabis.com/graphql/admin', headers=headers, json=json_data)

    data = response
    
    return data


if __name__ == "__main__":
    
    with st.form(key='log_in',):
        
        email = st.text_input('email:'),
        password_st = st.text_input('Password:',type='password')

        submitted = st.form_submit_button('Log in')

        try:
            if submitted:
                st.write('Credentials Saved')


                user = email[0]
                password = password_st
                token,user_id = get_bearer_token(user,password)
                headers = create_headers(token)
                
        except:
            st.warning('Incorrect Email or Password, Try again')

    file_uploaded = st.file_uploader('Please upload the file with the items you want to process.')

    if file_uploaded:
        user = email[0]
        password = password_st
        token,userid = get_bearer_token(user,password)
        headers = create_headers(token)

        file = load_dataframe(file_uploaded)
        df = file.dropna(subset=['OrgName'])
        df['dueDate'] = df['dueDate'].astype('str')
        # df['enforcedDeductible'] = df['enforcedDeductible'].astype('str')
        
        list_items = df.to_json(orient='records')
        list_items = json.loads(list_items)

        st.markdown(f'Total number of invoices to generate: {len(list_items)}')

        create_invs = st.button('Create Invoices')

        if create_invs:

            for i in list_items:
                Org_id = i['Org_id']
                dueDate = i['dueDate']
                amount = i['Amount']
                toggle = i['enforcedDeductible']
                notes = i['adminNotes']
                inv_id = i['InvoiceID']

                data = invoice_creation_AS(headers,Org_id,dueDate,amount=amount,toogle=toggle,notes=notes,invoice_id=inv_id)
                data
                st.markdown('---')
                if data['data']['postAccountingAPICreateManualInvoiceForOrg'] == True:
                    st.text(f'Invoice Generated')

                else:
                  st.write(data)
