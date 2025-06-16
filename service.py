# service.py
import requests
from bs4 import BeautifulSoup
import json
import re


def _parse_react_router_stream(html_text):
    """Attempt to extract serverResponse JSON from React Router streaming."""
    pieces = re.findall(r"streamController.enqueue\(\"(.*?)\"\)", html_text)
    if not pieces:
        return None

    joined = "".join(pieces)
    try:
        decoded = bytes(joined, "utf-8").decode("unicode_escape")
    except Exception:
        decoded = joined

    sr_match = re.search(r'"serverResponse":({.*?})', decoded)
    if not sr_match:
        return None
    try:
        return json.loads(sr_match.group(1))
    except json.JSONDecodeError:
        return None

def scrape_chatgpt_conversation(share_link):
    try:
        response = requests.get(share_link)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', string=re.compile('window.__remixContext'))
        data = None
        if script_tag:
            json_str = re.search(r'window\.__remixContext\s*=\s*({.*?});', script_tag.string, re.DOTALL)
            if json_str:
                data = json.loads(json_str.group(1))
        else:
            if soup.find('script', string=re.compile('window.__reactRouterContext')):
                server_response = _parse_react_router_stream(response.text)
                if server_response:
                    data = {'state': {'loaderData': server_response}}

        if not data:
            return None

        loader_data = data.get('state', {}).get('loaderData', {})
        meta_data = loader_data.get('meta', {})

        analysis = {
            'meta': {
                'title': meta_data.get('title'),
                'description': meta_data.get('description'),
                'image_src': meta_data.get('imageSrc'),
            },
            'user_info': {},
            'layer_summary': {
                layer_id: {
                    'is_active': layer.get('is_experiment_active'),
                    'is_user_in_experiment': layer.get('is_user_in_experiment'),
                    'parameters': layer.get('value', {})
                } for layer_id, layer in loader_data.get('layer_configs', {}).items()
            }
        }

        user_info = data.get('state', {}).get('user', {})
        if user_info:
            analysis['user_info'] = {
                'country': user_info.get('country'),
                'auth_status': user_info.get('custom', {}).get('auth_status'),
                'user_agent': user_info.get('userAgent'),
            }

        return analysis

    except requests.RequestException:
        return None


def extract_chat_messages_recursive(nodes, messages, mapping_data):
    for node in nodes:
        message = node.get('message', {})
        author = message.get('author', {}).get('role', 'unknown')
        content = message.get('content', {}).get('parts', [''])[0] if message.get('content') else ''
        timestamp = message.get('create_time', 'unknown')
        
        if content:
            messages.append({
                'author': author,
                'content': content,
                'timestamp': timestamp
            })
        
        children_ids = node.get('children', [])
        if children_ids:
            child_nodes = [mapping_data.get(child_id) for child_id in children_ids if child_id in mapping_data]
            child_nodes = [child for child in child_nodes if child]
            extract_chat_messages_recursive(child_nodes, messages, mapping_data)

def extract_chat_messages(share_link):
    try:
        response = requests.get(share_link)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', string=re.compile('window.__remixContext'))
        data = None
        if script_tag:
            json_str = re.search(r'window\.__remixContext\s*=\s*({.*?});', script_tag.string, re.DOTALL)
            if json_str:
                data = json.loads(json_str.group(1))
        else:
            if soup.find('script', string=re.compile('window.__reactRouterContext')):
                server_response = _parse_react_router_stream(response.text)
                if server_response:
                    data = {'state': {'loaderData': {'routes/share.$shareId.($action)': {'serverResponse': {'data': server_response}}}}}

        if not data:
            return None

        server_response = data.get('state', {}).get('loaderData', {}).get('routes/share.$shareId.($action)', {}).get('serverResponse', {}).get('data', {})
        
        if not server_response:
            return None
        
        mapping_data = server_response.get('mapping', {})
        linear_conversation_data = server_response.get('linear_conversation', [])
        
        chat_messages = []
        extract_chat_messages_recursive(linear_conversation_data, chat_messages, mapping_data)
        
        return chat_messages if chat_messages else None

    except requests.RequestException:
        return None

