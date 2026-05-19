# Gyűrűejtést elemző program

Ez a program egy komplex adatelemző eszköz, amely a gyűrűejtési kísérletek eredményeit dolgozza fel különböző anyagok (műanyag, fém, szappan) esetén. Az elemzést tartalmaz másodfokú regresszión alapuló elemzést és gépi tanulást is.

## Főbb funkciók

- **Előfeltételek:**
  Mielőtt elkezdenéd a program használatát, győződj meg róla, hogy a következő szoftverek telepítve vannak a gépeden:

  1.  **Python 3.x:**
      *   Látogass el a hivatalos Python weboldalra: [https://www.python.org/downloads/](https://www.python.org/downloads/)
      *   Töltsd le a legújabb stabil Python 3-as verziót.
      *   Futtasd a telepítőt, és **nagyon fontos**, hogy jelöld be a "Add Python to PATH" opciót a telepítés elején! Ez megkönnyíti a későbbi parancssori használatot.
      *   Fejezd be a telepítést.

  2.  **Visual Studio Code (VSCode):**
      *   Látogass el a VSCode weboldalára: [https://code.visualstudio.com/](https://code.visualstudio.com/)
      *   Töltsd le és telepítsd a VSCode-ot a rendszerednek megfelelően.
      *   A VSCode telepítése után érdemes lehet telepíteni a "Python" bővítményt (Microsoft által), amely számos hasznos funkciót biztosít a Python fejlesztéshez.

- **Statisztikai elemzés:** Átlagok és szórások számítása.
- **Gépi tanulás:** Random Forest modell használata a szarvmagasság előrejelzésére.
- **Kísérlettervezés:** Javaslatok tételése új mérési pontokra ott, ahol a modell bizonytalan vagy kevés az adat.
- **Interaktív vizualizáció:** Plotly alapú 3D térképek és válaszfelület kontúrdiagramok.
- **Riportkészítés:** Egyetlen, hordozható HTML jelentés generálása, amely PDF-be is menthető.

## Használat

1. Telepítsd a szükséges csomagokat a `requirements/requirements.txt` fájlból:
   ```bash
   pip install -r requirements/requirements.txt
   ```
2. Győződj meg róla, hogy az Excel forrásfájl elérhető a kódban megadott útvonalon.
3. Futtasd a Python szkriptet.
4. A program automatikusan megnyitja az elkészült `riport.html` fájlt a böngésződben.

## Kimenet
A jelentés a `C:\Python\Gyuru_Riport` mappába készül el, és ugyanitt egy ZIP archívum is létrejön a könnyebb megosztáshoz.
