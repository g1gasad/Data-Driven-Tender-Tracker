import pandas as pd

def PUSH_DATA_TO_SHEET(SERVICE, SPREADSHEET_ID, DATAFRAME, WORKSHEET_NAME_STRING):
    worksheet_name = WORKSHEET_NAME_STRING + "!"
    cell_range_insert = 'A1'
    columns = list(DATAFRAME.columns)
    data = []
    for row in DATAFRAME.iterrows():
        data.append(list(row[1]))
    values = ([columns] + data)
    value_range_body = {'majorDimension': "ROWS",
                        'values': values}
    SERVICE.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=WORKSHEET_NAME_STRING
            ).execute()
    return SERVICE.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        valueInputOption="USER_ENTERED",
                        range=worksheet_name + cell_range_insert,
                        body=value_range_body
                    ).execute()

def FETCH_DATA(SERVICE, SPREADSHEET_ID, OLD_SHEET_STRING, NEW_SHEET_STRING):
    mySpreadsheets = SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    old = SERVICE.spreadsheets().values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=OLD_SHEET_STRING,
                ).execute()
    new = SERVICE.spreadsheets().values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=NEW_SHEET_STRING,
                ).execute()
    old_df = pd.DataFrame(old['values'][1:], columns=old['values'][0])
    new_df = pd.DataFrame(new['values'][1:], columns=new['values'][0])
    return old_df, new_df

def VALIDATE_AND_UPDATE(OLD_DATAFRAME, NEW_DATAFRAME):
    stage_update_map = {"New!":1, "Yes":2, "No":3}
    merged_df = OLD_DATAFRAME.merge(NEW_DATAFRAME[['Tender_ID', 'Stage']],
                                     on='Tender_ID', suffixes=('', '_new'))
    indices_to_update = merged_df[merged_df['Stage'] != merged_df['Stage_new']].index
    OLD_DATAFRAME.loc[indices_to_update, 'Stage'] = merged_df.loc[indices_to_update, 'Stage_new']
    OLD_DATAFRAME['Updated'] = "No"
    OLD_DATAFRAME.loc[indices_to_update, 'Updated'] = "Yes"
    newly_added_list = list(set(NEW_DATAFRAME['Tender_ID']) - set(OLD_DATAFRAME['Tender_ID']))
    to_add = NEW_DATAFRAME[NEW_DATAFRAME['Tender_ID'].isin(newly_added_list)].reset_index(drop=True)
    to_add['Updated'] = "New!"
    updated_df = pd.concat([to_add, OLD_DATAFRAME], ignore_index=True)
    updated_df['stage_update_mapper'] = updated_df['Updated'].map(stage_update_map)
    updated_df = updated_df.sort_values(by="stage_update_mapper").drop("stage_update_mapper", axis=1)
    return updated_df


