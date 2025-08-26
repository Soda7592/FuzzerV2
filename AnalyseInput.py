from bs4 import BeautifulSoup
from colorama import Fore, Style, init
import json

def GetSelectOptions(select_tag):
    """
    從一個 BeautifulSoup <select> 標籤中提取所有 <option> 的值。
    
    Args:
        select_tag (BeautifulSoup.Tag): <select> 標籤物件。
        
    Returns:
        list: 包含所有 <option> value 的列表，如果沒有 value 則使用文本內容。
    """
    options_list = []
    # 在 <select> 標籤內部尋找所有 <option> 標籤
    options = select_tag.find_all('option')
    
    for option in options:
        # 優先使用 value 屬性，如果不存在，則使用選項的文本內容
        option_value = option.get('value', option.get_text(strip=True))
        options_list.append(option_value)
        
    return options_list

def GetInputInfo(all_bs_tags):
    """
    從 BeautifulSoup 標籤列表中，提取 <form> 和 <input> 等輸入欄位的詳細資訊。
    此版本已更新，能偵測 'required' 屬性。
    """
    print(f"\n{Fore.BLUE}--- 提取表單及輸入欄位資訊 ---{Style.RESET_ALL}")
    
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
                # 忽略提交類型按鈕
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
        
    print(f"{Fore.GREEN}成功提取 {len(forms_info)} 個表單的資訊。{Style.RESET_ALL}")
    return forms_info