from nicegui import ui
from pony.orm import Database, db_session, Required , PrimaryKey, select,Optional ,max
from datetime import date, datetime

db=Database()

class Transactions(db.Entity):
    
    index=PrimaryKey(int,auto=True)
    date=Optional(date)
    article=Required(str)
    beneficiaire=Required(str)
    montant=Required(float)
    
db.bind(provider='mysql',user='walidbm',password='Choukri13',host='mysql-walidbm.alwaysdata.net',db='walidbm_depense')
db.generate_mapping(create_tables=True)    
    
               

ui.add_head_html('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
     
@ui.page('/')
def main():
    with ui.card().classes() as cd_id:
        psw_le=ui.input('Mot de passe')
        psw_bt=ui.button('ok',on_click=lambda:psw(psw_le.value))
    
    db_dic=list()
        
    def psw(psw_str): 
        if psw_str =="Choukri13":
            with db_session:
                query=select(p for p in Transactions )
                for x in query:
                    ligne_dic={'id':x.index,'date':x.date,'article':x.article,'beneficiaire':x.beneficiaire,'montant':x.montant}
                    db_dic.append(ligne_dic)
            psw_le.delete()
            psw_bt.delete()
            cd_id.delete()
            table_gui.rows=db_dic.copy()
            table_gui.update()
            table_gui.visible=True
            mytabs.visible=True
            c_tab_p.visible=True
            
            
       
         
        
        
        # les tabs        
    with ui.column().classes('w-1/2 fixed top-0 right-0 m-4 bg-blue-100 shadow-lg p-4'):
        with ui.tabs() as mytabs:
            
            c_tab=ui.tab('c',label='Calculer dépenses')
            a_tab=ui.tab('a',label='Ajouter dépense')
            m_tab=ui.tab('m',label='Modifier dépense')
            s_tab=ui.tab('s',label='Supprimer dépense')
        
        with ui.tab_panels(tabs=mytabs,value='c').classes('w-full bg-blue-100 shadow-lg') as tab_tp:
            
            with ui.tab_panel(c_tab).classes() as c_tab_p:
                    with ui.row().classes() as r:
                        label1=ui.label('Somme=')
                        label2=ui.label('')
                        
                    bt=ui.button('Calculer',on_click= lambda:somme(table_gui))
            
            
            with ui.tab_panel(s_tab):
                with ui.element('div').classes():   
                    bt=ui.button('Supprimer Dépenses',on_click= lambda:supprimer(table_gui)).classes('justify-center-autop-2 bg-red-100')

                
                
            with ui.tab_panel(a_tab):
                date_input=ui.input('Date:')
                article_input=ui.input('Article:')
                beneficiaire_input=ui.input('Beneficiaire:')
                montant_input=ui.input('Montant:')    
                bt_add=ui.button('Ajouter',on_click= lambda:add(table_gui)) 
            with ui.tab_panel(m_tab):
                date_input_m=ui.input('Date:')
                article_input_m=ui.input('Article:')
                beneficiaire_input_m=ui.input('Beneficiaire:')
                montant_input_m=ui.input('Montant:')    
                bt_add_m=ui.button('Modifier',on_click= lambda :mod(table_gui))
                bt_add_m.disable()   
        mytabs.visible=False
        c_tab_p.visible=False
                    
    # dialog pour confirmer suppression                  
    """with ui.dialog() as dialog , ui.card():
        ui.label('Voulez vous vraiment supprimer le fichier')
        with ui.row().classes():
            ui.button(text='Oui',on_click=supprimer)
            ui.button(text='Non',on_click=lambda:dialog.close())"""

#la table    
    with ui.column().classes('w-1/2'):
        
        table_gui=ui.table(columns= [{'label':"id",'field':'id'},
                                    { 'label':'date','field':'date'},
                                    { 'label':'article','field':'article'},
                                    {'label':'beneficiaire','field':'beneficiaire'},
                                    {'label':'montant','field':'montant'}
                                    ],
                                    row_key='id',
                                    rows=db_dic,
                                    selection='multiple',
                                    on_select=lambda:tab_change(mytabs))  
        table_gui.visible=False
    def somme(table_gui):
        somme=0.0
        for x in table_gui.selected:
            somme+=float(x['montant'])
        somme=str(somme)+' DT'
        label2.set_text(somme)
    
    def add(table_gui):
        date_str=datetime.strptime(date_input.value, "%Y-%m-%d")
        with db_session:
            
            t=Transactions(date=date_str, article=article_input.value,
                        beneficiaire=beneficiaire_input.value,
                        montant=float(montant_input.value))
            last_id=max(p.index for p in Transactions)
            
            table_gui.add_rows ({'id':last_id,'date':t.date,
                                    'article':t.article,
                                    'beneficiaire':t.beneficiaire,
                                    'montant':t.montant})
 

    def supprimer(table_gui):               
        y=table_gui.selected.copy()
        for x in y:       
            table_gui.remove_rows({'id':x['id']})
            with db_session:
                q=Transactions.get(index= int( x['id']))
                q.delete()      
            ui.notify('Suppresion avec succées')
          

   
    def tab_change(mytabs):
        
        if tab_tp.value=='m':
            if len(table_gui.selected) == 1 :
                x=table_gui.selected[0]['id']
                date_input_m.set_value(table_gui.selected[0]['date'])
                article_input_m.set_value(table_gui.selected[0]['article'])
                beneficiaire_input_m.set_value(table_gui.selected[0]['beneficiaire'])
                montant_input_m.set_value(table_gui.selected[0]['montant'])
                bt_add_m.enable()
                
            elif len(table_gui.selected)>1:
                ui.notify('Veuillez selectionner une seule ligne')
                bt_add_m.disable()
            elif len(table_gui.selected)==0:
                date_input_m.set_value('')
                article_input_m.set_value('')
                beneficiaire_input_m.set_value('')
                montant_input_m.set_value('')
                bt_add_m.disable()
                    
    def mod(table_gui):
        selected_row=table_gui.selected[0].copy()
        id_mod=selected_row['id']
        date_str=datetime.strptime(date_input_m.value, "%Y-%m-%d")
        with db_session:
            Transactions[id_mod].date=date_str
            Transactions[id_mod].article=article_input_m.value
            Transactions[id_mod].beneficiaire=beneficiaire_input_m.value
            Transactions[id_mod].montant=montant_input_m.value
        
        for row_mod in table_gui.rows :
            if row_mod['id']==table_gui.selected[0]['id']:
                row_mod.update({'date': date_input_m.value,
                                'article': article_input_m.value,
                                'beneficiaire': beneficiaire_input_m.value,
                                'montant':montant_input_m.value})
                table_gui.update()
                break
    
  
    
"""      
def psw(user,password):
    if password =="Choukri13":
        db_dic=list()
        with db_session:
            query=select(p for p in Transactions )
            for x in query:
                ligne_dic={'id':x.index,'date':x.date,'article':x.article,'beneficiaire':x.beneficiaire,'montant':x.montant}
                db_dic.append(ligne_dic)
        table_gui.rows= db_dic.copy()
        login_dialog.close()
        return True
        
    

    
with ui.dialog() as login_dialog, ui.card():
    ui.label('Veuillez vous identifier').classes('text-lg')
    username_input = ui.input('Nom d\'utilisateur').classes('w-full')
    password_input = ui.input('Mot de passe',password=True).classes('w-full')  
    ui.button('Se connecter', on_click=lambda: psw(username_input.value, password_input.value))

# Afficher la boîte de dialogue dès le démarrage
login_dialog.open() 
"""
ui.run()
