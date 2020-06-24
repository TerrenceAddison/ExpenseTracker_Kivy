from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import sqlite3
from collections import OrderedDict

Builder.load_string('''
<DataTable>:
    id:main_table
    RecycleView:
        viewclass:'ItemLabel'
        id: table_top
        RecycleGridLayout:
            id:table_top_layout
            cols:5
            default_size:(None,250)
            default_size_hint:(1,None)
            size_hint_y: None
            height: self.minimum_height
            spacing:5
<ItemLabel@Label>:
    bcolor:(1,1,1,1)
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            size: self.size
            pos: self.pos
''')
class DataTable(BoxLayout):
    def __init__(self,table='',**kwargs):
        super().__init__(**kwargs)

        #entries = self.get_items()
        entries = table

        col_titles = [k for k in entries.keys()]
        row_length = len(entries[col_titles[0]])
        self.columns = len(col_titles)
        table_data = []
        for t in col_titles:
            table_data.append({'text':str(t),'size_hint_y':None,'height':30,'bcolor':(.25,.25,.8,1)})
        
        for r in range(row_length):
            for t in col_titles:
                table_data.append({'text':str(entries[t][r]),'size_hint_y':None,'height':30,'bcolor':(.25,.25,.7,1)})
        self.ids.table_top_layout.cols = self.columns
        self.ids.table_top.data = table_data
    

#class DataTableApp(App):
#    def build(self):
#
#        return DataTable()
#
#if __name__ == '__main__':
#    DataTableApp().run()