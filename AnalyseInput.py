from bs4 import BeautifulSoup
from colorama import Fore, Style, init
import json
from ParseArg import ParseBody

def GetSelectOptions(select_tag):
    options_list = []
    options = select_tag.find_all('option')
    
    for option in options:
        option_value = option.get('value', option.get_text(strip=True))
        options_list.append(option_value)
        
    return options_list

def GetInputInfo(all_bs_tags):
    # print(f"\n{Fore.BLUE}--- 提取表單及輸入欄位資訊 ---{Style.RESET_ALL}")
    
    forms_info = []

    forms = [tag for tag in all_bs_tags if tag.name == 'form']

    if not forms:
        print(f"{Fore.YELLOW}頁面中未偵測到 <form> 標籤。{Style.RESET_ALL}")
    
    for form_tag in forms:
        form_action = form_tag.get('action', '')
        form_method = form_tag.get('method', 'get').lower()
        
        input_fields = form_tag.find_all(['input', 'textarea', 'select'])
        
        fields_info = []
        for field in input_fields:
            field_name = field.get('name')
            
            if not field_name:
                continue
            
            field_type = field.get('type', 'text').lower()
            
            if field.name == 'select':
                # 專門處理 <select> 標籤
                field_info = {
                    'tag_name': field.name,
                    'name': field_name,
                    'type': 'select',
                    'id': field.get('id'),
                    'options': GetSelectOptions(field),
                    'required': 'required' in field.attrs # 這裡檢查 'required' 屬性
                }
            else:
                if field_type in ['submit', 'button', 'image', 'reset']:
                    continue
                
                # 檢查 'required' 屬性是否存在於標籤的屬性字典中
                is_required = 'required' in field.attrs
                
                field_info = {
                    'tag_name': field.name,
                    'name': field_name,
                    'type': field_type,
                    'id': field.get('id'),
                    'value': field.get('value', ''),
                    'placeholder': field.get('placeholder', ''),
                    'maxlength': field.get('maxlength'),
                    'required': is_required # 將偵測到的結果儲存
                }
            
            fields_info.append(field_info)
            
        forms_info.append({
            'action': form_action,
            'method': form_method,
            'fields': fields_info
        })
        
    # print(f"{Fore.GREEN}成功提取 {len(forms_info)} 個表單的資訊。{Style.RESET_ALL}")
    return forms_info

def BuildData(AllTags, url, body_str) :
    data = ParseBody(body_str)
    InputInfo = {}
    InputInfo[url] = GetInputInfo(AllTags)
    method = InputInfo[url][0]['method']
    NonEmpty_fields = {}
    for tag in InputInfo[url][0]['fields']:
        if tag['required'] == True:
            NonEmpty_fields[tag['name']] = tag
        elif tag['type'] == 'text' or tag['type'] == 'textarea' :
            NonEmpty_fields[tag['name']] = tag
    for key, value in NonEmpty_fields.items():
        if value['type'] == "text":
            data[key] = "test"
        elif value['type'] == "textarea":
            data[key] = "test"
        elif value['type'] == "select":
            data[key] = value['options'][0]
    return data, method