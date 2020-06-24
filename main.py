from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from datetime import datetime
from kivy.uix.boxlayout import BoxLayout
from collections import OrderedDict
from datatable import DataTable
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FCK 
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle



class MainWindow(Screen):        
    amount=ObjectProperty(None)
    category=ObjectProperty(None)
    message=ObjectProperty(None)

    
    def add_expense(self):

        
        tempcat = self.category.text
        tempamt = self.amount.text
        tempday = str(self.ids.expenseday.text)
        tempmonth = str(self.ids.expensemonth.text)
        tempyear = str(self.ids.expenseyear.text)

        if tempcat =='' or tempamt == '' or tempday == "Day" or tempmonth == "Month" or tempyear == "Year":
            self.error()
        else:
            self.confirmation()
            
    def quit(self):
        App.get_running_app().stop()
        Window.close()


    def confirmed_add(self, instance):
        tempday = str(self.ids.expenseday.text)
        tempmonth = str(self.ids.expensemonth.text)
        tempyear = str(self.ids.expenseyear.text)
        date = tempyear+"-"+tempmonth+"-"+tempday
        conn = sqlite3.connect("expenditure.db")
        cur = conn.cursor()
        cur.execute(""" INSERT INTO expenses (amount,category,message,date) VALUES (?,?,?,?)""", (self.amount.text,self.category.text,self.message.text,date))
        conn.commit()
        conn.close()
        self.amount.text=""
        self.category.text=""
        self.message.text=""

        self.parent.ids.scnd.ids.catsearch.clear_widgets()
        entry = self.parent.ids.scnd.itemlist.get_items(self)
        entrytable = DataTable(table=entry)
        target = self.parent.ids.scnd.ids.catsearch
        target.add_widget(entrytable)
        self.success()

    def confirmation(self):
        box = BoxLayout(orientation = 'vertical', padding = (10))
        box.add_widget(Label(text = "Once added it may be irreversible!"))
        popup = Popup(title='Are you sure?', title_size= (30), 
                  title_align = 'center', content = box,
                  size_hint=(None, None), size=(400, 400),
                  auto_dismiss = False)
        box.add_widget(Button(text = "OK",  on_press=self.confirmed_add, on_release=popup.dismiss))
        box.add_widget(Button(text = "NO",  on_press=popup.dismiss))
        
        popup.open()
    
    def error(self):
        box = BoxLayout(orientation = 'vertical', padding = (10))
        box.add_widget(Label(text = "Please fill in and select all fields!"))
        popup = Popup(title='Error', title_size= (30), 
                  title_align = 'center', content = box,
                  size_hint=(None, None), size=(400, 400),
                  auto_dismiss = False)
        box.add_widget(Button(text = "OK",  on_press=popup.dismiss))
        popup.open()
    
    def success(self):
        box = BoxLayout(orientation = 'vertical', padding = (10))
        box.add_widget(Label(text = "Expense has successfully been added"))
        popup = Popup(title='Success!', title_size= (30), 
                  title_align = 'center', content = box,
                  size_hint=(None, None), size=(400, 400),
                  auto_dismiss = False)
        box.add_widget(Button(text = "OK",  on_press=popup.dismiss))
        popup.open()
    





class SecondWindow(Screen):
    class categorysearch(Spinner):
        def __init__(self,**kwargs):
            super().__init__(**kwargs)
            
            
            conn = sqlite3.connect("expenditure.db")
            cur = conn.cursor()           
            sql = ("SELECT DISTINCT category FROM expenses;")
            cur.execute(sql)
            rows = cur.fetchall()
            cats =[]
            spinvals = []
            for i in rows:
                cats.append(i)
            for x in cats:
                temp = str(x)
                temp = temp[2:-3]
                spinvals.append(str(temp))
            spinvals.append("All")         
            self.values = spinvals
            print(self.text)

    def delete_item(self):
        target=self.ids.selectid.text
        conn = sqlite3.connect("expenditure.db")
        cur = conn.cursor()
        cur.execute('DELETE from expenses where id = ?',(target,))
        conn.commit()
        
        entry = self.ids.catsearch.get_items()
        entrytable = DataTable(table=entry)
        self.ids.catsearch.clear_widgets()
        self.ids.catsearch.add_widget(entrytable)
    
    
    def search_cat(self):
            target = self.ids.cat.text
            conn = sqlite3.connect("expenditure.db")
            cur = conn.cursor()
            _entries = OrderedDict()
            _entries['idlist'] ={}
            _entries['amountlist'] ={}
            _entries['categorylist'] ={}
            _entries['messagelist'] ={}
            _entries['datelist'] ={}
            idlist = []
            amountlist = []
            categorylist = []
            messagelist = []
            datelist = []
            rows = None
            if target == "All":
                cur.execute('SELECT * FROM expenses')
                rows = cur.fetchall()
            else:
                cur.execute('SELECT * FROM expenses WHERE category=?', (target,))
                rows = cur.fetchall()
            
            for id1,amt,cat,price,dt in rows:
                idlist.append(id1)
                amountlist.append(amt)
                categorylist.append(cat)
                messagelist.append(price)
                datelist.append(dt)
            entrynum = len(amountlist)
            idx = 0
            while idx < entrynum:
                _entries['idlist'][idx] = idlist[idx]
                _entries['amountlist'][idx] = amountlist[idx]
                _entries['categorylist'][idx] = categorylist[idx]
                _entries['messagelist'][idx] = messagelist[idx]
                _entries['datelist'][idx] = datelist[idx]

                idx +=1
        
            entrytable = DataTable(table=_entries)
            self.ids.catsearch.clear_widgets()
            self.ids.catsearch.add_widget(entrytable)

    class itemlist(BoxLayout):
        def __init__(self,**kwargs):
            super().__init__(**kwargs)

            entry = self.get_items()
            entrytable = DataTable(table=entry)
            self.add_widget(entrytable)


        def get_items(self):
            conn = sqlite3.connect("expenditure.db")
            cur = conn.cursor()
            _entries = OrderedDict()
            _entries['idlist'] ={}
            _entries['amountlist'] ={}
            _entries['categorylist'] ={}
            _entries['messagelist'] ={}
            _entries['datelist'] ={}
            idlist = []
            amountlist = []
            categorylist = []
            messagelist = []
            datelist = []
            sql = ("SELECT * FROM expenses;")
            cur.execute(sql)
            rows = cur.fetchall()
            for id1,amt,cat,price,dt in rows:
                idlist.append(id1)
                amountlist.append(amt)
                categorylist.append(cat)
                messagelist.append(price)
                datelist.append(dt)
            entrynum = len(amountlist)
            idx = 0
            while idx < entrynum:
                _entries['idlist'][idx] = idlist[idx]
                _entries['amountlist'][idx] = amountlist[idx]
                _entries['categorylist'][idx] = categorylist[idx]
                _entries['messagelist'][idx] = messagelist[idx]
                _entries['datelist'][idx] = datelist[idx]

                idx +=1
        
            return _entries

    

class ThirdWindow(Screen):
    class categories(Spinner):
        def __init__(self,**kwargs):
            super().__init__(**kwargs)
            
            conn = sqlite3.connect("expenditure.db")
            cur = conn.cursor()           
            sql = ("SELECT DISTINCT category FROM expenses;")
            cur.execute(sql)
            rows = cur.fetchall()
            cats =[]
            spinvals = []
            for i in rows:
                cats.append(i)
            for x in cats:
                temp = str(x)
                temp = temp[2:-3]
                spinvals.append(str(temp))
            self.values = spinvals

    def view_stats(self):
        plt.cla()
        self.ids.analysis_res.clear_widgets()
        target_category=self.ids.cat.text
        print(target_category)
        conn = sqlite3.connect("expenditure.db")
        cur = conn.cursor()           
        cur.execute('SELECT amount,date FROM expenses WHERE category=?', (target_category,))
        rows = cur.fetchall()
        purchases = []
        dates = []
        for amt,dt in rows:
            purchases.append(amt)
            dates.append(dt)
        plt.bar(dates,purchases,color='#131d86',label="Expenditures")
        plt.ylabel('Total Purchases')
        plt.xlabel('day')

        self.ids.analysis_res.add_widget(FCK(plt.gcf()))

        

class FourthWindow(Screen):
        def search_date(self):
            if str(self.ids.day_input.text) == "Day" or str(self.ids.month_input.text) == "Month" or str(self.ids.year_input.text) == "Year":
                self.error("Please select all fields!")
            else:
                day = str(self.ids.day_input.text)
                month = str(self.ids.month_input.text)
                year = str(self.ids.year_input.text)
                conn = sqlite3.connect("expenditure.db")
                cur = conn.cursor()
                cur.execute("""SELECT sum(amount) FROM expenses where strftime('%m', date) = ? and strftime('%Y', date) = ?  and  strftime('%d',date) = ?; """, (month,year,day))
                daytotal = cur.fetchone()[0]
                cur.execute("""SELECT sum(amount) FROM expenses where strftime('%m', date) = ? and strftime('%Y', date) = ?; """, (month,year))
                monthtotal = cur.fetchone()[0]
                cur.execute("""SELECT sum(amount) FROM expenses where strftime('%Y', date) = ?; """, (year,))
                yeartotal = cur.fetchone()[0]
                if daytotal == None:
                    self.ids.daily.text = "No transactions made on this day!"
                else:
                    self.ids.daily.text = "$" + str(daytotal)

                if monthtotal == None:
                    self.ids.monthly.text = "No transactions made on this month!"
                else:
                    self.ids.monthly.text = "$" + str(monthtotal)
                if yeartotal == None:
                    self.ids.yearly.text = "No transactions made on this year!"
                else:
                    self.ids.yearly.text = "$" + str(yeartotal)

 
                
        
        def error(self,errortext=""):
            box = BoxLayout(orientation = 'vertical', padding = (10))
            box.add_widget(Label(text = errortext))
            popup = Popup(title='Error', title_size= (30), 
                    title_align = 'center', content = box,
                    size_hint=(None, None), size=(400, 400),
                    auto_dismiss = False)
            box.add_widget(Button(text = "OK",  on_press=popup.dismiss))
            popup.open()









def view(category=None):

    conn = db.connect("expenditure.db")
    cur = conn.cursor()
    if category:
        sql = '''
        select * from expenses where category = '{}'
        '''.format(category)
        sql2 = '''
        select sum(amount) from expenses where category = '{}'
        '''.format(category)
    else:
        sql = '''
        select * from expenses
        '''.format(category)
        sql2 = '''
        select sum(amount) from expenses
        '''.format(category)
    cur.execute(sql)
    results = cur.fetchall()
    cur.execute(sql2)
    total_amount = cur.fetchone()[0]

    return total_amount, results



class WindowManager(ScreenManager):
    pass





class MyMainApp(App):
    
    def build(self):
        self.title = 'Xpense Tracker'
        conn = sqlite3.connect("expenditure.db")
        cur = conn.cursor()
        sql = """
        create table if not exists expenses (
            id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            amount number,
            category string,
            message string,
            date string
            );
        """
        cur.execute(sql)
        conn.commit()
        kv = Builder.load_file("my.kv")
        return kv
    
    


if __name__ == "__main__":
    MyMainApp().run()