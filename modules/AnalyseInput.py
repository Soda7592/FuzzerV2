from bs4 import BeautifulSoup
from colorama import Fore, Style, init
import json
from .ParseArg import ParseBody
from urllib.parse import urljoin, urlparse
from collections import defaultdict

def GetSelectOptions(select_tag):
    options_list = []
    options = select_tag.find_all('option')
    
    for option in options:
        option_value = option.get('value', option.get_text(strip=True))
        options_list.append(option_value)
        
    return options_list

# def MergeSameAction(forms_info):
#     if not forms_info:
#         return []

#     grouped = defaultdict(lambda: {
#         'action': None,
#         'method': None,
#         'fields_dict': {}  # 用來去重：name -> field
#     })

#     for form in forms_info:
#         key = form['action']
#         group = grouped[key]

#         # 第一次遇到這個 action，設定基本資訊
#         if group['action'] is None:
#             group['action'] = form['action']
#             group['method'] = form['method']

#         # 合併 fields，依 name 去重（後面覆蓋前面）
#         for field in form['fields']:
#             group['fields_dict'][field['name']] = field

#     # 轉回原本格式
#     merged_forms = []
#     for group in grouped.values():
#         merged_forms.append({
#             'action': group['action'],
#             'method': group['method'],
#             'fields': list(group['fields_dict'].values())  # 轉成 list
#         })

#     return merged_forms

# def HasDuplicateActions(forms_info):
#     if not forms_info:
#         return False
#     seen = set()
#     for form in forms_info:
#         action = form.get('action')
#         if action in seen:
#             return True
#         seen.add(action)
#     return False

def GetInputInfo(all_bs_tags):
    # print(f"\n{Fore.BLUE}--- 提取表單及輸入欄位資訊 ---{Style.RESET_ALL}")
    forms_info = []

    forms = [tag for tag in all_bs_tags if tag.name == 'form']
    # print(forms)
    if not forms:
        # print(all_bs_tags)
        print(f"{Fore.YELLOW}頁面中未偵測到 <form> 標籤。{Style.RESET_ALL}")
        # print(all_bs_tags)
        return None
    
    # http://192.168.11.129:8080/administrator/index.php?option=com_users&view=level&layout=edit

    # print("Found Forms:")

    for form_tag in forms:
        form_action = form_tag.get('action', '')
        form_method = form_tag.get('method', 'get').lower()
        
        input_fields = form_tag.find_all(['select', 'textarea', 'input'])
        
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
    # print(f"{Fore.RED}forms_info: {forms_info}{Style.RESET_ALL}")
    # forms_info = MergeSameAction(forms_info)
    #print(f"{Fore.RED}forms_info: {forms_info}{Style.RESET_ALL}")
    # if HasDuplicateActions(forms_info):
    #     forms_info = MergeSameAction(forms_info)
    return forms_info

def BuildData(AllTags, url, body_str) :
    data = ParseBody(body_str)
    protocol = urlparse(url).scheme
    domain = urlparse(url).netloc
    preurl = protocol + "://" + domain
    InputInfo = {}
    InputInfo[url] = GetInputInfo(AllTags)
    if InputInfo[url] is None:
        return None, None
    method = InputInfo[url][0]['method']
    NonEmpty_fields = {}
    # print(url)
    # for tag in InputInfo[url]:
    #     print(tag)
    target = None
    # print(InputInfo[url])
    for tag in InputInfo[url]:
        act = tag['action']
        # print(f"{Fore.RED}act: {act}{Style.RESET_ALL}")
        # print(f"{Fore.YELLOW}urljoin(preurl, act): {urljoin(preurl, act)}{Style.RESET_ALL}")
        # print(f"{Fore.GREEN}url: {url}{Style.RESET_ALL}")
        if urljoin(preurl, act) == url:
            target = tag
            # print(f"{Fore.GREEN}target: {target}{Style.RESET_ALL}")
            break
    if target is None:
        # print(f"{Fore.BLUE}target is None{Style.RESET_ALL}")
        return None, None
    # print(url)
    # print(target['fields'])
    # print(target['fields'])
    # for tag in target['fields']: # in InputInfo[url][0]['fields']:
    #     if tag['required'] == True:
    #         NonEmpty_fields[tag['name']] = tag
    #     elif tag['type'] == 'text' or tag['type'] == 'textarea' :
    #         NonEmpty_fields[tag['name']] = tag
    for tag in target['fields']:
        if tag['required'] == True:
            data[tag['name']] = "Fuzzable"
        elif tag['type'] == 'text' or tag['type'] == 'textarea':
            data[tag['name']] = "Fuzzable"
        elif tag['type'] == 'select':
            data[tag['name']] = tag['options'][0]
        elif tag['tag_name'] == 'textarea':
            data[tag['name']] = "Fuzzable"
    # print(NonEmpty_fields)

    # for key, value in NonEmpty_fields.items():
    #     # print(value)
    #     if value['type'] == "text":
    #         data[key] = "Fuzzable"
    #         # print(key)
    #     elif value['type'] == "textarea":
    #         data[key] = "Fuzzable"
    #     elif value['type'] == "select":
    #         data[key] = value['options'][0]
    
    # for key, value in data.items():
    #     print(key, value)

    return data, method