import streamlit as st
import json
import os

# ページ設定
st.set_page_config(
    page_title="TODO アプリ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# タイトル
st.title("📝 TODO アプリ")

# セッション状態の初期化
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# データ保存ファイルのパス
DATA_FILE = "todos.json"

# JSONファイルから既存データを読み込む
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# タスクをJSONファイルに保存
def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# アプリ起動時にデータを読み込む
if not st.session_state.tasks:
    st.session_state.tasks = load_tasks()

# タスク入力と追加ボタン
col1, col2 = st.columns([4, 1])
with col1:
    task_input = st.text_input(
        "新しいタスクを入力してください",
        key="task_input",
        placeholder="例: Streamlitアプリを完成させる"
    )
with col2:
    add_button = st.button("追加", use_container_width=True)

# 追加ボタンが押された時
if add_button and task_input.strip():
    new_task = {
        "id": len(st.session_state.tasks),
        "title": task_input.strip(),
        "done": False
    }
    st.session_state.tasks.append(new_task)
    save_tasks(st.session_state.tasks)
    st.rerun()

# フィルター設定
st.divider()

# Issue #5: タスクのフィルター表示機能
# ステータスに応じたタスク表示のフィルタリングを実装
filter_option = st.radio(
    "表示するタスク",
    ["すべて", "未完了", "完了"],
    horizontal=True
)

# フィルタリング
if filter_option == "未完了":
    filtered_tasks = [t for t in st.session_state.tasks if not t["done"]]
elif filter_option == "完了":
    filtered_tasks = [t for t in st.session_state.tasks if t["done"]]
else:
    filtered_tasks = st.session_state.tasks

# タスク表示
if filtered_tasks:
    st.subheader(f"タスク一覧 ({len(filtered_tasks)}件)")
    for idx, task in enumerate(filtered_tasks):
        col1, col2, col3 = st.columns([0.5, 4, 0.5])
        
        with col1:
            # チェックボックス
            is_done = st.checkbox(
                "完了",
                value=task["done"],
                key=f"checkbox_{task['id']}"
            )
            if is_done != task["done"]:
                task["done"] = is_done
                save_tasks(st.session_state.tasks)
                st.rerun()
        
        with col2:
            # タスク表示（完了時は打ち消し線）
            if task["done"]:
                st.write(f"~~{task['title']}~~")
            else:
                st.write(task['title'])
        
        with col3:
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{task['id']}", use_container_width=True):
                st.session_state.tasks.remove(task)
                save_tasks(st.session_state.tasks)
                st.rerun()
else:
    st.info("タスクがありません。新しいタスクを追加してください！")

# 統計情報
st.divider()
if st.session_state.tasks:
    completed_count = len([t for t in st.session_state.tasks if t["done"]])
    total_count = len(st.session_state.tasks)
    completion_rate = (completed_count / total_count) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("全体", total_count)
    with col2:
        st.metric("完了", completed_count)
    with col3:
        st.metric("完了率", f"{completion_rate:.0f}%")
