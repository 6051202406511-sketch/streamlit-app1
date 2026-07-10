import streamlit as st
import json
import os
from datetime import datetime, timedelta

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

# タスクに経過時間を計算する関数
def get_elapsed_time(task):
    """タスクの経過時間（秒）を計算"""
    if 'created_at' not in task or 'duration_seconds' not in task:
        return 0
    
    created_at = datetime.fromisoformat(task['created_at'])
    elapsed = (datetime.now() - created_at).total_seconds()
    return max(0, elapsed)

# 残り時間をフォーマットする関数
def format_remaining_time(remaining_seconds):
    """残り時間をフォーマット（例：5分23秒）"""
    if remaining_seconds <= 0:
        return "0秒"
    
    minutes = int(remaining_seconds // 60)
    seconds = int(remaining_seconds % 60)
    
    if minutes > 0:
        return f"{minutes}分{seconds}秒"
    else:
        return f"{seconds}秒"

# 進捗率を計算する関数
def get_progress(task):
    """タスクの進捗率を計算（0.0～1.0）"""
    if 'duration_seconds' not in task or task['duration_seconds'] is None:
        return None
    
    elapsed = get_elapsed_time(task)
    progress = elapsed / task['duration_seconds']
    return min(1.0, progress)  # 最大1.0

# アプリ起動時にデータを読み込む
if not st.session_state.tasks:
    st.session_state.tasks = load_tasks()

# タスク入力と追加ボタン
st.subheader("新しいタスクを追加")
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    task_input = st.text_input(
        "タスク名",
        key="task_input",
        placeholder="例: Streamlitアプリを完成させる"
    )

with col2:
    duration_minutes = st.number_input(
        "実行時間（分）",
        min_value=0,
        max_value=600,
        value=0,
        step=1,
        key="duration_input",
        help="0 を選択すると、タイマー無しのタスクになります"
    )

with col3:
    add_button = st.button("追加", use_container_width=True)

# 追加ボタンが押された時
if add_button and task_input.strip():
    new_task = {
        "id": len(st.session_state.tasks),
        "title": task_input.strip(),
        "done": False,
        "duration_seconds": int(duration_minutes * 60) if duration_minutes > 0 else None,
        "created_at": datetime.now().isoformat()
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
    
    # 自動完了ロジック: 時間が経過したタスクを自動で完了にする
    # （全タスクをチェック、フィルター前に処理）
    has_auto_completed = False
    for task in st.session_state.tasks:
        # 未完了で、タイマー付きで、時間に達したタスクを自動完了
        if (not task.get("done") and 
            task.get("duration_seconds") is not None and
            task.get("created_at") is not None):
            
            elapsed = get_elapsed_time(task)
            if elapsed >= task["duration_seconds"]:
                task["done"] = True
                has_auto_completed = True
    
    # 自動完了が発生した場合のみ保存
    if has_auto_completed:
        save_tasks(st.session_state.tasks)
    
    for idx, task in enumerate(filtered_tasks):
        col1, col2, col4 = st.columns([0.5, 3.5, 0.5])
        
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
            # タスク表示とタイマー
            if task["done"]:
                st.write(f"~~{task['title']}~~")
            else:
                # タイマー付きタスクの表示
                if task.get("duration_seconds") is not None and task.get("created_at") is not None:
                    elapsed = get_elapsed_time(task)
                    remaining = max(0, task["duration_seconds"] - elapsed)
                    remaining_text = format_remaining_time(remaining)
                    progress = get_progress(task)
                    
                    # タスク名と残り時間を表示
                    st.write(f"{task['title']} **⏱ 残り時間: {remaining_text}**")
                    
                    # プログレスバーを表示
                    st.progress(progress, text=f"{progress*100:.0f}%")
                else:
                    # タイマー無しのタスク
                    st.write(task['title'])
        
        with col4:
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

# タイマー付きタスクが存在する場合は自動更新を推奨
has_timer_tasks = any(t.get("duration_seconds") is not None and not t.get("done") for t in st.session_state.tasks)
if has_timer_tasks:
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("⏱ アクティブなタイマーがあります。より正確な時間表示のため定期的にリロードしてください。")
    with col2:
        if st.button("🔄 今すぐ更新", use_container_width=True):
            st.rerun()
