import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import learning_curve
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import shap
import warnings
import os
import base64
import io
import shutil
from tqdm import tqdm
import webbrowser
import seaborn as sns
import plotly.graph_objects as go
import plotly.offline as pyo

# Elrejtjük a technikai jellegű figyelmeztetéseket, hogy a futási eredmények átláthatóbbak legyenek.
warnings.filterwarnings('ignore')

def get_base64_plot():
    # Ez a függvény az éppen elkészült grafikont alakítja át egy speciális szöveges formátummá.
    # Ez azért szükséges, hogy a képet közvetlenül be tudjuk építeni a HTML jelentésbe, külön fájl nélkül.
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_str

def create_analysis():
    # Megadjuk az adatok forrását és a feldolgozni kívánt munkalapok nevét.
    excel_path = r"C:\Python\Gyuru\Adatok\Gyűrűejtés adattábla.xlsx"
    sheets = ["Műanyag", "Fém", "Szappan"]

    # Létrehozzuk a mappát a riport számára, ha még nem létezik.
    output_dir = r"C:\Python\Gyuru_Riport"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Meghatározzuk, milyen oszlopneveket keresünk az adatok között.
    search_features = ['külső sugár', 'belső sugár', 'vastagság', 'tömeg', 'ejtési magasság']
    target_keyword = 'szarv magasság'
    
    name_mapping = {
        "Műanyag": "Muanyag",
        "Fém": "Fem",
        "Szappan": "Szappan"
    }
    
    # Beolvassuk a megjelenítéshez szükséges JavaScript kódokat.
    plotly_js = pyo.get_plotlyjs()

    # Előkészítjük a HTML fájl vázát és a kinézetet meghatározó stíluslapokat.
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Gyűrűejtés Elemzési Riport</title>
    <script>{plotly_js}</script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }}
        h1 {{ text-align: center; color: #2c3e50; margin-left: 220px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px; }}
        
        /* Segítünk a böngészőnek, hogy szép PDF-et generáljon a nyomtatáskor */
        @media print {{
            .sidebar, .theme-toggle, .print-btn {{ display: none !important; }}
            .container {{ margin-left: 0 !important; max-width: 100% !important; }}
            body {{ background-color: white !important; color: black !important; }}
            .chart-card {{ box-shadow: none !important; border: 1px solid #eee !important; page-break-inside: avoid; }}
            h1 {{ margin-left: 0 !important; }}
        }}

        .container {{ max-width: 1000px; margin-left: 240px; }}
        .chart-card {{ background: #ffffff; padding: 20px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
        .stats-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; }}
        .stats-table th, .stats-table td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: center; }}
        .stats-table th {{ background-color: #2c3e50; color: white; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ecf0f1; border-radius: 4px; }}
        p.caption {{ font-size: 15px; color: #7f8c8d; margin-top: 15px; font-style: italic; }}
        
        /* Az oldalsó menüsáv kialakítása */
        .sidebar {{ width: 210px; position: fixed; top: 0; left: 0; height: 100vh; background-color: #2c3e50; padding-top: 20px; color: white; z-index: 100; overflow-y: auto; }}
        .sidebar h3 {{ padding: 0 15px; font-size: 11px; text-transform: uppercase; color: #95a5a6; margin-top: 25px; margin-bottom: 10px; letter-spacing: 1px; }}
        .sidebar button, .sidebar a {{ display: block; width: 100%; padding: 10px 15px; text-decoration: none; color: #bdc3c7; background: none; border: none; text-align: left; cursor: pointer; font-size: 14px; transition: 0.2s; }}
        .sidebar button:hover, .sidebar a:hover {{ background-color: rgba(255,255,255,0.1); color: white; }}
        .sidebar button.active {{ background-color: #3498db; color: white; font-weight: bold; }}
        .sidebar .nav-group {{ border-bottom: 1px solid #3e4f5f; padding-bottom: 15px; margin-bottom: 5px; }}
        .tabcontent {{ display: none; padding: 0; background-color: transparent; }}
        .print-btn {{ padding: 15px; border-top: 1px solid #3e4f5f; }}
    </style>
    /* A menüváltást és az oldalon belüli ugrásokat kezelő kódok */
    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].style.display = "none"; }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
            window.scrollTo(0, 0);
        }}
        function jumpTo(section) {{
            var activeTab = document.querySelector('.tabcontent[style*="display: block"]');
            if (activeTab) {{
                var targetId = activeTab.id + "-" + section;
                var element = document.getElementById(targetId);
                if (element) {{
                    var headerOffset = 20;
                    var elementPosition = element.getBoundingClientRect().top;
                    var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    window.scrollTo({{ top: offsetPosition, behavior: "smooth" }});
                }}
            }}
        }}
        window.onload = function() {{ 
            document.getElementsByClassName('tablinks')[0].click();
        }};
    </script>
</head>
<body>
    <div class="sidebar">
        <div class="print-btn"><button onclick="window.print()" style="background: #27ae60; color: white; text-align: center; border-radius: 4px; width: 100%; border: none; padding: 10px; cursor: pointer; font-weight: bold;">📄 Mentés PDF-ként</button></div>
        <h3>Anyagok</h3>
        <div class="nav-group">
"""
    # Dinamikusan feltöltjük a menüt az anyagokkal.
    for sheet in sheets:
        display_name = sheet[0].upper() + sheet[1:].lower()
        html_content += f'            <button class="tablinks" onclick="openTab(event, \'{display_name}\')">{display_name}</button>\n'
    
    html_content += """        </div>
        <h3>Elemzések</h3>
        <a onclick="jumpTo('stats')">📊 Statisztika</a>
        <a onclick="jumpTo('corr')">🔗 Korreláció</a>
        <a onclick="jumpTo('thickness')">📏 Vastagságfüggés</a>
        <a onclick="jumpTo('importance')">🏆 Változók fontossága</a>
        <a onclick="jumpTo('error')">🎯 Hiba-elemzés</a>
        <a onclick="jumpTo('metrics')">📈 Pontosság</a>
        <a onclick="jumpTo('extremes')">↔️ Szélsőértékek</a>
        <a onclick="jumpTo('doe')">💡 Kísérlettervezési javaslatok</a>
        <a onclick="jumpTo('doe3d')">🌐 3D kísérleti térkép</a>
        <a onclick="jumpTo('lc')">⏳ Tanulási görbe</a>
        <a onclick="jumpTo('shap')">🧬 Összetett hatáselemzés</a>
        <a onclick="jumpTo('rsm')">🌀 Válaszfelület elemzés</a>
    </div>
    <div class="container">
        <h1>Gyűrűejtés - ML és RSM elemzési riport</h1>
"""

    for sheet in tqdm(sheets, desc="Feldolgozás"):
        # Beolvassuk az aktuális munkalapot.
        df = pd.read_excel(excel_path, sheet_name=sheet)

        # Egységesítjük a mértékegységeket és megtisztítjuk az oszlopneveket.
        column_renames = {}
        for col in df.columns:
            col_lower = col.lower()
            is_feature = any(f in col_lower for f in search_features)
            is_target = target_keyword in col_lower
            
            if is_feature or is_target:
                df[col] = df[col] * 1000
                clean_name = col.split(' (')[0].split(' [')[0]
                clean_name = clean_name[0].upper() + clean_name[1:].lower()
                unit = " [g]" if "Tömeg" in clean_name else " [mm]"
                column_renames[col] = clean_name + unit
        
        df.rename(columns=column_renames, inplace=True)

        # Kiválogatjuk a modellhez szükséges bemeneti és célváltozókat.
        actual_features = []
        for feat in search_features:
            match = [col for col in df.columns if feat in col.lower()]
            if match:
                actual_features.append(match[0])
        
        target_match = [col for col in df.columns if target_keyword in col.lower()]
        actual_target = target_match[0] if target_match else target_keyword

        X = df[actual_features]
        y = df[actual_target]
        
        sheet_display_name = sheet[0].upper() + sheet[1:].lower()
        safe_name = name_mapping.get(sheet, sheet.lower()).lower()
        html_content += f'<div id="{sheet_display_name}" class="tabcontent">\n<h2>{sheet_display_name} anyag elemzése</h2>\n'
        
        # Kiszámítjuk az alapvető statisztikai adatokat.
        stats = X.agg(['mean', 'std']).T
        stats.columns = ['Átlag', 'Szórás']
        stats_html = stats.to_html(classes='stats-table', float_format=lambda x: f"{x:.2f}")
        html_content += f"""
        <div id="{sheet_display_name}-stats" class="chart-card">
            <p style="font-size: 18px; color: #2c3e50; margin-bottom: 10px;"><b>Kísérleti beállítások átlaga és szórása</b></p>
            {stats_html}
            <p class="caption">A táblázat a kísérleti beállítások (bemeneti paraméterek) átlagát és szórást mutatja az adott anyagra vonatkozóan.</p>
        </div>\n"""

        # Megvizsgáljuk, mennyire függnek össze a változók a célváltozóval.
        corr = df[actual_features + [actual_target]].corr()
        target_corr_data = corr[[actual_target]].drop(actual_target).sort_values(by=actual_target, ascending=False)
        
        plt.figure(figsize=(10, 3))
        sns.heatmap(target_corr_data.T, annot=True, cmap='RdYlGn', center=0, fmt="+.2f")
        plt.title(f'{sheet_display_name} - korreláció a célváltozóval', fontsize=12)
        plt.tight_layout()
        corr_base64 = get_base64_plot()

        html_content += f"""
        <div id="{sheet_display_name}-corr" class="chart-card">
            <a href="data:image/png;base64,{corr_base64}" target="_blank"><img src="data:image/png;base64,{corr_base64}" alt="Target Correlation" loading="lazy"></a>
            <p class="caption"><b>Korrelációs elemzés:</b> az ábra kifejezetten a(z) <b>{actual_target}</b> célváltozó és a bemeneti paraméterek közötti lineáris kapcsolatot mutatja.</p>
        </div>\n"""

        # Külön elemzést készítünk a vastagság és a szarvmagasság kapcsolatáról.
        thick_col_list = [c for c in actual_features if 'vastagság' in c.lower()]
        if thick_col_list:
            thick_col = thick_col_list[0]
            
            fig_thick = go.Figure()
            
            fig_thick.add_trace(go.Scatter(
                x=X[thick_col], 
                y=y, 
                mode='markers', 
                marker=dict(color='purple', opacity=0.6, size=10),
                name='Mért adatok',
                hovertemplate=f"{thick_col}: %{{x:.2f}}<br>{actual_target}: %{{y:.2f}}<extra></extra>"
            ))
            
            z = np.polyfit(X[thick_col], y, 2)
            p = np.poly1d(z)
            x_range = np.linspace(X[thick_col].min(), X[thick_col].max(), 100)
            
            fig_thick.add_trace(go.Scatter(
                x=x_range, 
                y=p(x_range), 
                mode='lines', 
                line=dict(color='red', dash='dash'),
                name='Trendvonal (másodfokú)',
                hoverinfo='skip'
            ))
            
            fig_thick.update_layout(
                title=f'{sheet_display_name} - szarvmagasság függése a vastagságtól',
                xaxis_title=thick_col,
                yaxis_title=actual_target,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            thick_plotly_html = fig_thick.to_html(full_html=False, include_plotlyjs=False)
            
            html_content += f'<div id="{sheet_display_name}-thickness" class="chart-card">{thick_plotly_html}<p class="caption"><b>Vastagságfüggés:</b> Az interaktív diagram a(z) <b>{thick_col}</b> és a(z) <b>{actual_target}</b> közötti összefüggést mutatja. Húzd az egeret a pontok fölé a pontos értékekért!</p></div>\n'

        # Tanítunk egy véletlen erdő (Random Forest) modellt, hogy lássuk, melyik változó a legfontosabb.
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        importances = rf.feature_importances_
        indices = np.argsort(importances)[::-1]
        sorted_features = [actual_features[i] for i in indices]
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(X.shape[1]), importances[indices], color='steelblue')
        plt.xticks(range(X.shape[1]), sorted_features, rotation=15)
        plt.title(f'{sheet_display_name} - paraméterek befolyásoló ereje', fontsize=14)
        plt.ylabel('Fontosság mértéke')
        plt.tight_layout()
        rf_base64 = get_base64_plot()
        
        html_content += f'<div id="{sheet_display_name}-importance" class="chart-card"><a href="data:image/png;base64,{rf_base64}" target="_blank"><img src="data:image/png;base64,{rf_base64}" alt="Importance" loading="lazy"></a><p class="caption">Ez az ábra azt mutatja meg, hogy melyik paraméter változtatása van a legnagyobb hatással a végeredményre.</p></div>\n'
        
        # Összehasonlítjuk a modell jóslatait a tényleges mérési eredményekkel.
        # Biztosítjuk, hogy a jósolt magasság ne legyen negatív, mert az fizikailag lehetetlen.
        y_pred = np.maximum(0, rf.predict(X))
        
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        plt.figure(figsize=(8, 8))
        plt.scatter(y, y_pred, alpha=0.6, color='darkcyan', edgecolors='k')
        plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
        plt.xlabel(f'Mért {actual_target}')
        plt.ylabel(f'Modell által jósolt {actual_target}')
        plt.title(f'{sheet_display_name} - hiba-elemzés (mért vs jósolt)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        pred_base64 = get_base64_plot()

        html_content += f'<div id="{sheet_display_name}-error" class="chart-card"><a href="data:image/png;base64,{pred_base64}" target="_blank"><img src="data:image/png;base64,{pred_base64}" alt="Actual vs Predicted" loading="lazy"></a><p class="caption"><b>Hiba-elemzési ábra:</b> a modell predikciói 0-ra vannak korlátozva a fizikai realitás megőrzése érdekében.</p></div>\n'

        # Megnézzük, hol voltak a legkisebb és legnagyobb mért értékek.
        idx_min = y.idxmin()
        idx_max = y.idxmax()
        y_min_act, y_min_pred = y.loc[idx_min], np.maximum(0, rf.predict(X.loc[[idx_min]])[0])
        y_max_act, y_max_pred = y.loc[idx_max], np.maximum(0, rf.predict(X.loc[[idx_max]])[0])

        html_content += f"""
        <div id="{sheet_display_name}-metrics" class="chart-card">
            <p style="font-size: 18px; color: #2c3e50;"><b>Modell pontossági mutatói:</b></p>
            <p>R² érték (meghatározási együttható): <b>{r2:.4f}</b></p>
            <p>RMSE (gyökátlagos négyzetes hiba): <b>{rmse:.4f}</b> {actual_target.split(' [')[1] if ' [' in actual_target else ''}</p>
        </div>
        
        <div id="{sheet_display_name}-extremes" class="chart-card">
            <p style="font-size: 18px; color: #2c3e50;"><b>Szélsőérték predikciók:</b></p>
            <div style="text-align: left; display: inline-block; width: 90%;">
                <p><b>Minimum szarvmagasság esete:</b><br>
                Beállítások: <i>{", ".join([f"{c}: {X.loc[idx_min, c]:.2f}" for c in actual_features])}</i><br>
                Mért érték: <b>{y_min_act:.2f}</b> | Modell predikció: <b>{y_min_pred:.2f}</b></p>
                
                <p><b>Maximum szarvmagasság esete:</b><br>
                Beállítások: <i>{", ".join([f"{c}: {X.loc[idx_max, c]:.2f}" for c in actual_features])}</i><br>
                Mért érték: <b>{y_max_act:.2f}</b> | Modell predikció: <b>{y_max_pred:.2f}</b></p>
            </div>
        </div>\n"""

        # Kiszámítjuk, hova érdemes tenni a következő méréseket.
        # Ehhez 2000 véletlenszerű pontot generálunk, és keressük a "fehér foltokat".
        n_candidates = 2000
        mins = X.min()
        maxs = X.max()
        np.random.seed(42)
        candidates = pd.DataFrame(
            np.random.uniform(mins, maxs, size=(n_candidates, len(actual_features))),
            columns=actual_features
        )

        # Távolság alapú ritkaság számítása (Exploration)
        scaler_doe = MinMaxScaler()
        X_scaled = scaler_doe.fit_transform(X)
        candidates_scaled = scaler_doe.transform(candidates)
        
        nn = NearestNeighbors(n_neighbors=1).fit(X_scaled)
        distances, _ = nn.kneighbors(candidates_scaled)
        distances = distances.flatten()

        # Modell bizonytalanság számítása (Exploitation)
        # Az erdő fáinak egyedi predikciói közötti szórás (std)
        tree_preds = np.stack([t.predict(candidates.values) for t in rf.estimators_])
        uncertainties = np.std(tree_preds, axis=0)

        # Kombinált pontszám: normalizált távolság + normalizált bizonytalanság
        dist_norm = (distances - distances.min()) / (distances.max() - distances.min() + 1e-9)
        unc_norm = (uncertainties - uncertainties.min()) / (uncertainties.max() - uncertainties.min() + 1e-9)
        doe_score = dist_norm + unc_norm

        # Top 5 javaslat kiválasztása
        top_doe_idx = np.argsort(doe_score)[-5:][::-1]
        doe_table_df = candidates.iloc[top_doe_idx].copy()
        doe_table_df['Bizonytalanság [mm]'] = uncertainties[top_doe_idx]
        doe_html = doe_table_df.to_html(classes='stats-table', float_format=lambda x: f"{x:.2f}", index=False)

        html_content += f"""
        <div id="{sheet_display_name}-doe" class="chart-card">
            <p style="font-size: 18px; color: #2c3e50; margin-bottom: 10px;"><b>Szekvenciális kísérlettervezési (DoE) javaslatok</b></p>
            {doe_html}
            <p class="caption"><b>Módszertan:</b> A szoftver 2000 elméleti pontot vizsgált meg. A táblázat azokat a helyeket javasolja új mérésre, ahol vagy túl ritka a jelenlegi mintavételezés (távol esik a többi ponttól), vagy ahol a modell becslése a legbizonytalanabb.</p>
        </div>\n"""

        # --- 3c. 3D DoE Vizualizáció ---
        if len(sorted_features) >= 3:
            f1, f2, f3 = sorted_features[0], sorted_features[1], sorted_features[2]
            
            # Predikció a DoE pontokra a színezéshez
            doe_preds = np.maximum(0, rf.predict(doe_table_df[actual_features]))
            
            fig_3d = go.Figure()
            
            # Jelenlegi pontok
            fig_3d.add_trace(go.Scatter3d(
                x=X[f1], y=X[f2], z=X[f3],
                mode='markers',
                marker=dict(
                    size=4, 
                    color=y, 
                    colorscale='Viridis', 
                    showscale=True,
                    colorbar=dict(title=dict(text=actual_target, font=dict(size=10)), thickness=15),
                    opacity=0.6
                ),
                name='Jelenlegi mérések'
            ))
            
            # DoE pontok
            fig_3d.add_trace(go.Scatter3d(
                x=doe_table_df[f1], y=doe_table_df[f2], z=doe_table_df[f3],
                mode='markers',
                marker=dict(size=8, color=doe_preds, colorscale='Viridis', symbol='diamond', opacity=0.9),
                name='Javasolt DoE pontok'
            ))
            
            fig_3d.update_layout(
                title=f"DoE térbeli eloszlás: {sheet_display_name}",
                scene=dict(
                    xaxis_title=f1,
                    yaxis_title=f2,
                    zaxis_title=f3
                ),
                margin=dict(l=0, r=0, b=0, t=40),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            
            doe_3d_html = fig_3d.to_html(full_html=False, include_plotlyjs=False)
            html_content += f'<div id="{sheet_display_name}-doe3d" class="chart-card">{doe_3d_html}<p class="caption"><b>3D DoE vizualizáció:</b> a kék pontok a meglévő méréseket, a piros gyémántok pedig a modell által javasolt új kísérleti helyszíneket jelölik a három legfontosabb paraméter terében.</p></div>\n'

        # --- 4. Tanulási görbe ---
        train_sizes, train_scores, test_scores = learning_curve(
            RandomForestRegressor(n_estimators=100, random_state=42), X, y, cv=5, scoring='r2')
        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', color="r", label="Tanító pontosság")
        plt.plot(train_sizes, np.mean(test_scores, axis=1), 'o-', color="g", label="Keresztvalidációs pontosság")
        plt.title(f'{sheet_display_name} - tanulási görbe', fontsize=14)
        plt.xlabel('Tanító minták száma')
        plt.ylabel('R² pontosság')
        plt.legend(loc="best")
        plt.grid(True)
        plt.tight_layout()
        lc_base64 = get_base64_plot()

        html_content += f'<div id="{sheet_display_name}-lc" class="chart-card"><a href="data:image/png;base64,{lc_base64}" target="_blank"><img src="data:image/png;base64,{lc_base64}" alt="Learning Curve" loading="lazy"></a><p class="caption"><b>Tanulási görbe.</b></p></div>\n'

        # Egy fejlettebb módszerrel (SHAP) elemezzük a változók hatásának irányát.
        explainer = shap.TreeExplainer(rf)
        shap_values = explainer.shap_values(X)
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, show=False)
        plt.title(f'{sheet_display_name} - Változók hatásának részletes elemzése', fontsize=14)
        plt.tight_layout()
        shap_base64 = get_base64_plot()
        
        shap_desc = f"""
        <div id="{sheet_display_name}-shap" class="chart-card">
            <a href="data:image/png;base64,{shap_base64}" target="_blank"><img src="data:image/png;base64,{shap_base64}" alt="SHAP Plot" loading="lazy"></a>
            <p class="caption"><b>Hogyan értelmezzük ezt az ábrát?</b><br>
            • <b>Függőleges tengely:</b> A paraméterek fontossági sorrendje (felül a legfontosabb).<br>
            • <b>Vízszintes tengely:</b> A hatás iránya. A 0-tól jobbra lévő pontok növelik, a balra lévők csökkentik a kimenetet ({actual_target}).<br>
            • <b>Szín (Kék-Piros):</b> A paraméter értéke. A <b>piros</b> a magas, a <b>kék</b> az alacsony értéket jelöli.<br>
            <i>Példa: Ha a piros pontok a jobb oldalon csoportosulnak, akkor a paraméter növelése növeli a szarv magasságát.</i></p>
        </div>"""
        html_content += shap_desc
        
        # Interaktív válaszfelület térképet készítünk, ahol bármely két paraméter együttes hatása vizsgálható.
        import itertools
        pairs = list(itertools.combinations(actual_features, 2))
        
        fig = go.Figure()
        buttons = []
        
        for i, (feat_x, feat_y) in enumerate(pairs):
            X_pair = X[[feat_x, feat_y]]
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X_pair)
            lr = LinearRegression().fit(X_poly, y)
            
            x_range = np.linspace(X_pair[feat_x].min(), X_pair[feat_x].max(), 30)
            y_range = np.linspace(X_pair[feat_y].min(), X_pair[feat_y].max(), 30)
            xx, yy = np.meshgrid(x_range, y_range)
            
            grid_df = pd.DataFrame(np.c_[xx.ravel(), yy.ravel()], columns=[feat_x, feat_y])
            zz = np.maximum(0, lr.predict(poly.transform(grid_df)).reshape(xx.shape))
            
            visible = (i == 0)
            fig.add_trace(go.Contour(
                z=zz, x=x_range, y=y_range,
                colorscale='Viridis', name=f"{feat_x} vs {feat_y}",
                visible=visible,
                colorbar=dict(title=dict(text=actual_target, font=dict(size=12)))
            ))
            
            visible_list = [False] * len(pairs)
            visible_list[i] = True
            buttons.append(dict(
                label=f"{feat_x.split(' (')[0]} - {feat_y.split(' (')[0]}",
                method="update",
                args=[{"visible": visible_list},
                      {"xaxis": {"title": {"text": feat_x}}, 
                       "yaxis": {"title": {"text": feat_y}},
                       "title": f"Interaktív válaszfelület: {sheet_display_name} ({feat_x.split(' [')[0]} vs {feat_y.split(' [')[0]})"}]
            ))

        fig.update_layout(
            updatemenus=[dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.0, xanchor="left", y=1.15, yanchor="top"
            )],
            title=f"Interaktív válaszfelület: {sheet_display_name}",
            xaxis_title=pairs[0][0],
            yaxis_title=pairs[0][1],
            width=800, height=600,
            margin=dict(t=100)
        )
        
        plotly_html = fig.to_html(full_html=False, include_plotlyjs=False)
        html_content += f'<div id="{sheet_display_name}-rsm" class="chart-card">{plotly_html}<p class="caption">Interaktív válaszfelület. A legördülő menüvel válthatod ki, melyik két paraméter együttes hatását szeretnéd vizsgálni.</p></div>\n'
        
        html_content += "</div>\n"

    html_content += """
    </div>
</body>
</html>"""

    # Elmentjük az elkészült jelentést.
    report_path = os.path.join(output_dir, "riport.html")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Összecsomagoljuk a riportot egyetlen archívumba a könnyebb továbbíthatóságért.
    shutil.make_archive(output_dir, 'zip', output_dir)

    print(f"\nFeldolgozás befejezve! A riport sikeresen létrejött: {os.path.abspath(report_path)}")
    print(f"A hordozható ZIP archívum elkészült: {output_dir}.zip")

    # Megnyitjuk a jelentést a rendszer alapértelmezett böngészőjében.
    webbrowser.open('file://' + report_path)

if __name__ == "__main__":
    create_analysis()
