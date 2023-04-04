import streamlit as st
import toml
import pandas as pd
import snowflake.connector as sf
from datetime import date
import plotly.express as px
import plotly.graph_objects as go


# Connect to Snowflake
sidebar = st.sidebar

def connect_to_snowflake(usr, pwd, acct, rl, wh, db):
    conn = sf.connect(user=usr, password=pwd, account=acct, role=rl, warehouse=wh, database=db)
    cur = conn.cursor()
    st.session_state['connection'] = conn
    st.session_state['cursor'] = cur
    return conn, cur

with sidebar:
    default_name = "AGASHMURTHY"
    username= st.text_input("Username",default_name)
    default_pass="Agash062021"
    password=st.text_input("Password",default_pass , type="password")
    default_acc="rm70744.ap-southeast-1"
    account =st.text_input("Account",default_acc)
    default_rl='ACCOUNTADMIN'
    role=st.text_input("Role",default_rl)
    default_wh='COMPUTE_WH'
    wh=st.text_input("Warehouse",default_wh)
    default_db='PRACTICE'
    db=st.text_input("Database",default_db)
    if 'connection'not in st.session_state:
       connect=st.button("connect to snowflake",on_click=connect_to_snowflake,args=[username,password,account, role,wh,db])
 #disconnect
    if 'connection' in st.session_state:
      disconnect_button = st.button("Disconnect from Snowflake")
    
      if disconnect_button and 'connection' in st.session_state:
        conn = st.session_state['connection']
        conn.close()
        st.write("Disconnected from Snowflake")
        del st.session_state['connection']
        del st.session_state['cursor']
# Select table

if 'connection' in st.session_state:

    conn = st.session_state['connection']
    cur = st.session_state['cursor']
    
    schema_name = st.sidebar.selectbox("Select a schema", ['CSV_LOAD'])
    st.write(f"Selected schema: {schema_name}")

    # list of tables
    if schema_name == 'PRIVATE':
        tables = ['CUSTOMER', 'STORE']
    elif schema_name == 'CSV_LOAD':
        tables = ['MYSTORETABLE']
    elif schema_name == 'PROTECTED':
        tables = ['STUDENT', 'CUSTOMER']
        
    #table list
    table_name = st.sidebar.selectbox("Select a table", tables)
    
    # the selected table
    query = f"SELECT * FROM {schema_name} . {table_name}"
    cur.execute(query)
    rows = cur.fetchall()
    
    # Display table
   
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    st.write("Selected schema:", schema_name)
    st.write("Selected table:", table_name)

    st.markdown("<h1 style='text-align: center;'><b>Super Store Dashboard</b></h1>", unsafe_allow_html=True)

    x_column = 'REGION'
    index = df.columns.get_loc(x_column)
    x = x_column

    y_column = "PROFIT"
    index = df.columns.get_loc(y_column)
    y = y_column

    fig1= px.bar(df, x=x_column, y=y_column)

    st.write('Region-wise Sales and profit')
    region_profit = df.groupby('REGION')['PROFIT'].sum()
    st.write(region_profit)
    st.plotly_chart(fig1)

    #column = 'Sales' 
    column = 'SALES'
    index = df.columns.get_loc(column)
    x = column

#column= order date
    default_column = 'ORDER_DATE'
    default_index=df.columns.get_loc(default_column)
    y=default_column

    fig2= px.bar(df,x=x,y=y)

    st.write('Sales vs Order Date')
    top_10_dates = df.groupby('ORDER_DATE')['SALES'].sum().sort_values(ascending=True).tail(10)
    df_top_10_dates = df[df['ORDER_DATE'].isin(top_10_dates.index)]
    fig2 = px.bar(df_top_10_dates, x='ORDER_DATE', y='SALES', title='Sales for Top 10 Dates')
    fig2.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig2)
