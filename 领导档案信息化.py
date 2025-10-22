# app_web_flat.py
import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data(path, sheet):
    return pd.read_excel(path, sheet_name=sheet)

class ArchiveWebSystem:
    def __init__(self):
        self.excel_path = r"D:\.东方航空 工作\2025-09\领导档案信息化\档案信息化.xlsm"
        self.sheet_name = "档案清单"
        self.data = load_data(self.excel_path, self.sheet_name)

    # ---------- 工具 ----------
    def _detect_name_column(self):
        for c in self.data.columns:
            if any(k in c for k in ("姓名", "名字", "人员")):
                return c
        return None

    # ---------- 页面 ----------
    def run(self):
        st.set_page_config(page_title="档案管理系统", page_icon="📁", layout="wide")
        st.title("📁 档案管理系统")
        st.markdown("---")

        name_col = self._detect_name_column()
        if not name_col:
            st.error("未找到姓名列"); return

        # 全员列表
        all_names = sorted(self.data[name_col].dropna().unique())

        # 平铺布局：左 30% 搜索 / 列表，右 70% 详情
        left, right = st.columns([1, 3])

        with left:
            st.subheader("🔍 快速查询")
            keyword = st.text_input("输入姓名关键词", placeholder="支持模糊搜索")
            if keyword:
                show_names = [n for n in all_names if keyword in n]
            else:
                show_names = all_names

            st.metric("人员数量", len(all_names))
            st.markdown("---")
            st.write("**人员列表**")
            for i, name in enumerate(show_names, 1):
                if st.button(f"{i}. {name}", key=f"btn_{name}", use_container_width=True):
                    st.session_state["selected"] = name

        with right:
            if st.session_state.get("selected"):
                self.display_person(st.session_state["selected"])
            else:
                st.info("👈 请在左侧选择或搜索人员，即可查看完整档案")

    # ---------- 个人详情 ----------
    def display_person(self, name):
        name_col = self._detect_name_column()
        person = self.data[self.data[name_col] == name].iloc[0]

        tab1, tab2, tab3 = st.tabs(["📋 基本信息", "💼 工作信息", "📄 完整档案"])
        with tab1: self.display_basic_info(person)
        with tab2: self.display_work_info(person)
        with tab3: self.display_full_info(person)

    def display_basic_info(self, person):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 个人基本信息")
            for label, key in {"姓名":"姓名","性别":"性别","出生年月":"出生年月",
                               "民族":"民族","籍贯":"籍贯","出生地":"出生地"}.items():
                val = "未填写" if pd.isna(person.get(key)) else str(person.get(key))
                st.text_input(label, val, disabled=True)

        with col2:
            st.subheader("🎓 教育背景")
            for label, key in {"全日制学历":"全日制学历","全日制学位":"全日制学位",
                               "全日制毕业院校":"全日制毕业院校","全日制专业":"全日制专业",
                               "在职学历":"在职学历","在职学位":"在职学位",
                               "在职毕业院校":"在职毕业院校","在职专业":"在职专业"}.items():
                val = "未填写" if pd.isna(person.get(key)) else str(person.get(key))
                st.text_input(label, val, disabled=True)

        # 简历独占一行
        st.subheader("📄 简历")
        resume = "未填写" if pd.isna(person.get("简历")) else str(person["简历"])
        st.text_area("简历内容", resume, height=150, disabled=True, label_visibility="collapsed")

        # 家庭主要关系独占一行
        st.subheader("👨‍👩‍👧‍👦 家庭主要关系")
        family = "未填写" if pd.isna(person.get("家庭主要关系")) else str(person["家庭主要关系"])
        st.text_area("家庭关系", family, height=150, disabled=True, label_visibility="collapsed")
    def display_work_info(self, person):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💼 职务信息")
            for label, key in {"现任职务":"现任职务","拟任职务":"拟任职务","拟免职务":"拟免职务"}.items():
                st.text_input(label, person.get(key, "未填写"), disabled=True)
        with col2:
            st.subheader("📊 其他信息")
            for label, key in {"专业技术职务":"专业技术职务","熟悉专业有何专长":"熟悉专业有何专长",
                               "奖惩情况":"奖惩情况","年度考核结果":"年度考核结果"}.items():
                st.text_input(label, person.get(key, "未填写"), disabled=True)

    def display_full_info(self, person):
        st.subheader("📄 完整档案信息")
        details = [{"字段": k, "值": v} for k, v in person.items() if pd.notna(v) and str(v).strip()]
        if details:
            st.dataframe(pd.DataFrame(details), use_container_width=True, hide_index=True)
        else:
            st.info("暂无完整档案信息")

# -------------------- 启动 --------------------
if __name__ == "__main__":
    # 初始化 session
    if "selected" not in st.session_state:
        st.session_state.selected = None
    app = ArchiveWebSystem()
    app.run()