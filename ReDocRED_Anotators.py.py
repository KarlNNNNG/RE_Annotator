import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import random

# 实体类别及其颜色映射
ENTITY_COLORS = {
    "PER": "lightgreen",
    "ORG": "lightblue",
    "LOC": "lightyellow",
    "MISC": "lightpink",
    # 其他实体类型可以在这里添加
}

class TextAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本标注软件")

        
        # 设置主窗口的布局框架
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 第一步：导入文本
        self.load_button = tk.Button(self.main_frame, text="加载文本", command=self.load_text, bg="#009688", fg="white", padx=10)
        self.load_button.grid(row=0, column=0, pady=10, columnspan=2, sticky="w")

        # 文本显示框
        self.text_display = tk.Text(self.main_frame, height=25, width=80, font=("Arial", 14))
        self.text_display.grid(row=1, column=1, columnspan=4, pady=10)

        # 第二步：标注共指组
        self.add_segment_button = tk.Button(self.main_frame, text="添加到共指组", command=self.add_to_coreference_group, bg="#4CAF50", fg="white", padx=10)
        self.add_segment_button.grid(row=2, column=0, pady=10)

        # 实体标签的下拉菜单选项
        self.entity_label_options = ["ORG", "PER", "TIME", "LOC", "MISC"]
        self.entity_label_variable = tk.StringVar(self.main_frame)
        self.entity_label_variable.set(self.entity_label_options[0])  # 默认选中第一个选项

        # 创建实体标签的下拉菜单
        self.label_label = tk.Label(self.main_frame, text="实体标签:", font=("Arial", 10))
        self.label_label.grid(row=2, column=1, padx=(10, 0))

        self.entity_label_menu = tk.OptionMenu(self.main_frame, self.entity_label_variable, *self.entity_label_options)
        self.entity_label_menu.grid(row=2, column=2, padx=(10, 0))

        # 标注共指组按钮
        self.create_coreference_button = tk.Button(self.main_frame, text="标注共指组", command=self.assign_entity_to_coreference_group, bg="#2196F3", fg="white", padx=10)
        self.create_coreference_button.grid(row=2, column=3, pady=10)

        # 关系标注的部分
        self.relations_label = tk.Label(self.main_frame, text="输入两个实体的索引来标注关系:", font=("Arial", 10))
        self.relations_label.grid(row=4, column=0, columnspan=4, pady=(10, 0))

        self.relation_input1_label = tk.Label(self.main_frame, text="头实体索引:", font=("Arial", 10))
        self.relation_input1_label.grid(row=5, column=0, sticky="e")
        self.relation_input1 = tk.Entry(self.main_frame, width=5)
        self.relation_input1.grid(row=5, column=1, sticky="w")

        self.relation_input2_label = tk.Label(self.main_frame, text="尾实体索引:", font=("Arial", 10))
        self.relation_input2_label.grid(row=5, column=2, sticky="e")
        self.relation_input2 = tk.Entry(self.main_frame, width=5)
        self.relation_input2.grid(row=5, column=3, sticky="w")
        # 关系类别标注的下拉框
        self.relation_options = ['head of government', 'country', 'place of birth', 'place of death', 'father', 'mother', 'spouse', 'country of citizenship', 'head of state', 'capital', 'official language', 'position held', 'child', 'author', 'member of sports team', 'director', 'screenwriter', 'educated at', 'composer', 'member of political party', 'employer', 'founded by', 'league', 'publisher', 'owned by', 'religion', 'headquarters location', 'cast member', 'producer', 'award received', 'creator', 'parent taxon', 'ethnic group', 'performer', 'manufacturer', 'developer', 'series', 'sister city', 'legislative body', 'military branch', 'record label', 'production company', 'location', 'subclass of', 'subsidiary', 'part of', 'original language of work', 'original network', 'member of', 'chairperson', 'country of origin', 'has part', 'residence', 'conflict', 'characters', 'lyrics by', 'located on terrain feature', 'participant', 'influenced by', 'location of formation', 'parent organization', 'notable work', 'separated from', 'work location', 'participant of', 'replaces', 'replaced by', 'capital of', 'sibling']
        self.search_entry = tk.Entry(self.root)
        # 设置搜索框的位置
        #self.search_entry.pack(pady=10)    
        self.search_entry.place(x=1000, y=600, width=200, height=30)
        self.search_entry.bind('<KeyRelease>', self.update_listbox)  # 绑定搜索事件
        
        # 创建列表框
        self.listbox = tk.Listbox(self.root,height=10)
        self.listbox.place(x=1000, y=650, width=200, height=200)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        # self.listbox.pack(pady=10)

        # 显示所有选项
        self.update_listbox()
        # 添加 span 标注输入框
        self.span_label = tk.Label(self.main_frame, text="Span 标注:", font=("Arial", 10))
        self.span_label.grid(row=6, column=0, padx=(10, 0), pady=5, sticky="e")
        self.span_entry = tk.Entry(self.main_frame, width=20)
        self.span_entry.grid(row=6, column=1, pady=5, sticky="w")

        # 关系证据的输入框
        self.evidence_label = tk.Label(self.main_frame, text="证据句子索引 (用逗号分隔):", font=("Arial", 10))
        self.evidence_label.grid(row=6, column=2, sticky="e")
        self.evidence_entry = tk.Entry(self.main_frame)
        self.evidence_entry.grid(row=6, column=3, sticky="w")

        # 标注关系按钮
        self.annotate_relation_button = tk.Button(self.main_frame, text="标注关系", command=self.annotate_relation, bg="#FF9800", fg="white", padx=10)
        self.annotate_relation_button.grid(row=7, column=3, pady=10)

        # 底部的功能按钮：导出、清除
        self.export_button = tk.Button(self.main_frame, text="导出结果", command=self.export_results, bg="#795548", fg="white", padx=10)
        self.export_button.grid(row=8, column=0, pady=10, columnspan=2)

        self.clear_button = tk.Button(self.main_frame, text="清除标注", command=self.clear_annotations, bg="#F44336", fg="white", padx=10)
        self.clear_button.grid(row=8, column=2, columnspan=2)

        # 侧边列表显示共指组及标签或颜色
        self.coref_group_list = tk.Listbox(self.main_frame, height=20, width=40)
        self.coref_group_list.grid(row=0, column=6, rowspan=8, padx=10, pady=10)
        # 垂直滚动条
        self.yscroll = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.coref_group_list.yview)
        self.yscroll.grid(row=0, column=7, rowspan=8, sticky='ns')

        # 水平滚动条
        self.xscroll = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.coref_group_list.xview)
        self.xscroll.grid(row=8, column=6, sticky='ew')

        # 将滚动条绑定到 Listbox
        self.coref_group_list.config(yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set)

        # 允许 Listbox 显示长内容时进行水平滚动
        self.coref_group_list.config(width=40)  # 设置 Listbox 的宽度
        self.coref_group_list.grid(row=0, column=6, rowspan=8, padx=10, pady=10, sticky='nsew')


        self.sentences = []  # 存储切分后的句子
        self.entities = {}  # 存储实体标签和共指组
        self.coreference_groups = []  # 用于存储共指消解的实体组
        self.relations = []  # 存储共指组之间的关系
        self.current_coreference_group = []  # 临时存储当前共指组中的片段
        self.title_entry = ""
        self.full_text = ""
        self.span_info = {}
    
    def update_listbox(self, event=None):
        """根据输入动态更新列表框的内容"""
        search_term = self.search_entry.get().lower()
        self.listbox.delete(0, tk.END)  # 清空列表框
        for option in self.relation_options:
            if search_term in option.lower():  # 根据输入过滤选项
                self.listbox.insert(tk.END, option)  # 插入匹配的选项

    def on_select(self, event):
        """将列表框中选中的值显示到文本框中"""
        selection = self.listbox.curselection()
        if selection:
            selected_value = self.listbox.get(selection[0])  # 获取选中的值
            self.search_entry.delete(0, tk.END)  # 清空文本框
            self.search_entry.insert(0, selected_value)  # 在文本框中显示选中的值
            self.relation_variable = selected_value
    
    def load_text(self):
        """
        加载文本并按照 '|||' 进行切分，显示带索引的句子
        """
        self.entity_num = 0
        self.coreference_groups_num = 0
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.title_entry = file_path[:-4]
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                self.full_text = text
                self.sentences = text.split("|||")  # 按照 '|||' 切分文本

                # 清空显示框，按索引显示每个句子
                self.text_display.delete(1.0, tk.END)
                for i, sentence in enumerate(self.sentences):
                    self.text_display.insert(tk.END, f"{i}: {sentence.strip()}\n")
    
    def find_word_span(self, sentence, char_start, char_end):
        words = sentence.split()  # 将句子按空格拆分为单词
        word_spans = []  # 用于存储每个单词的字符范围

        current_pos = 0  # 当前字符位置的指针
        for word in words:
            word_start = current_pos  # 当前单词的起始位置
            word_end = word_start + len(word)  # 当前单词的结束位置

            word_spans.append((word_start, word_end))  # 记录单词的字符范围
            current_pos = word_end + 1  # 更新下一个单词的起始位置 (加1是为了跳过空格)

        # 查找给定的字符跨度包含的单词
        start_word_index = None
        end_word_index = None

        for i, (start, end) in enumerate(word_spans):
            if start_word_index is None and start <= char_start < end:
                start_word_index = i
            if end_word_index is None and start < char_end <= end:
                end_word_index = i

        # 如果找到了相应的单词范围
        if start_word_index is not None and end_word_index is not None:
            return start_word_index, end_word_index
        else:
            return None  # 如果没有找到对应的单词

    def add_to_coreference_group(self):
        try:
            selected_text = self.text_display.selection_get()
            start_index = self.text_display.index(tk.SEL_FIRST)
            end_index = self.text_display.index(tk.SEL_LAST)

            # 获取句子的索引
            sentence_idx = int(start_index.split(".")[0])

            # 获取句子内容并切分为单词
            sentence = self.sentences[sentence_idx-1] # 获取完整句子

            # 解析 start 和 end 的字符索引
            char_start = int(start_index.split(".")[1])-3
            char_end = int(end_index.split(".")[1])-3
            start_word_index, end_word_index = self.find_word_span(sentence, char_start, char_end)
            

            entity_segment = {
                "type": self.entity_label_variable.get(),
                "pos": [start_word_index, end_word_index+1],
                "name": selected_text,
                "sent_id": sentence_idx,
                "index": self.entity_num,
                "gold_index": str(self.coreference_groups_num) + "_" + str(self.entity_num)
            }
            self.entity_num += 1
            self.current_coreference_group.append(entity_segment)

            tag_id = f"CorefTemp-{start_index}-{end_index}"
            self.text_display.tag_add(tag_id, start_index, end_index)
            self.text_display.tag_config(tag_id, background="lightgray", foreground="black")

        except tk.TclError:
            messagebox.showwarning("选择错误", "请先选择文本进行标注")



    def assign_entity_to_coreference_group(self):
        """
        将当前共指组分配一个实体标签，并显示在侧边列表中
        """
        label = self.entity_label_variable.get()

        if not label:
            messagebox.showwarning("输入错误", "请提供一个实体标签")
            return

        if not self.current_coreference_group:
            messagebox.showwarning("实体对为空", "请先选择文本片段并添加到共指组")
            return

        group_id = f"Coref-{len(self.coreference_groups)}"
        self.coreference_groups.append({
            "group_id": group_id,
            "label": label,
            "entities": self.current_coreference_group
        })

        # 更新侧边列表，显示共指组及内容
        for i in range(len(self.current_coreference_group)):
            self.coref_group_list.insert(tk.END, f"索引: {self.current_coreference_group[i]['index']}, 标签: {label}, 内容: {self.current_coreference_group[i]['name']}, 位置: {self.current_coreference_group[i]['pos']}, 属于句子: {self.current_coreference_group[i]['sent_id']}")        
        
        messagebox.showinfo("共指组关系标注成功", f"共指组 '{group_id}' 已被标注为 '{label}'")
        # 清空当前共指组
        self.current_coreference_group = []

    def annotate_relation(self):
        """标注两个共指组之间的关系，并添加evidence"""
        try:
            index1 = int(self.relation_input1.get())
            index2 = int(self.relation_input2.get())
            relation_label = self.search_entry.get()
            evidence_input = self.evidence_entry.get()
            span_input = self.span_entry.get()

            if span_input not in self.span_info.keys():
                self.span_info[span_input] = 1
            else:
                self.span_info[span_input] += 1
                
            evidence_indices = [int(e.strip()) for e in evidence_input.split(",") if e.strip().isdigit()]

            relation = {
                "r": relation_label,
                "h": index1,
                "t": index2,
                "evidence": evidence_indices,
                "span": span_input       #这里要改一下，改成直接从两个index去索引sent_id  self.coreference_groups 里面的entity_segment就可以用index1和index2来标注span
            }
            self.relations.append(relation)
            messagebox.showinfo("关系标注成功", f"已标注实体组 '{index1}' 和 '{index2}' 之间的关系 '{relation_label}' 跨度为 '{span_input}'")

        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的数字索引")

    def export_results(self):
        """导出结果，包含共指组信息和实体在句子中的索引"""
        if not self.coreference_groups and not self.relations:
            messagebox.showwarning("导出错误", "没有可导出的标注")
            return
        
        results = {
            "title": self.title_entry,
            "vertexSet": [group["entities"] for group in self.coreference_groups],
            "labels": self.relations,
            "sents": [sentence.split() for sentence in self.sentences]
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(results, json_file, indent=4)
            messagebox.showinfo("导出成功", f"标注已导出至 {file_path}")

    def clear_annotations(self):
        self.text_display.tag_delete("all")
        self.entities = {}
        self.coreference_groups = []
        self.relations = []
        self.current_coreference_group = []
        self.coref_group_list.delete(0, tk.END)
        self.entity_num = 0
        self.coreference_groups_num = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = TextAnnotationApp(root)
    root.mainloop()
