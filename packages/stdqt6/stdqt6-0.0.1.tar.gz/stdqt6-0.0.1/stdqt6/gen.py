if __name__ == '__main__':
    from PyQt6 import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtMultimedia import *
    from PyQt6.QtNetwork import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *
    from PyQt6.QtXml import *
    from PyQt6.QtWebSockets import *
    from PyQt6.QtWebChannel import *
    from PyQt6.QtTextToSpeech import *
    from PyQt6.QtTest import *
    from PyQt6.QtSvg import *
    from PyQt6.QtSql import *
    from PyQt6.QtSerialPort import *
    from PyQt6.QtSensors import *
    from PyQt6.QtRemoteObjects import *
    from PyQt6.QtQuick import *
    from PyQt6.QtQuickWidgets import *
    from PyQt6.QtQuick3D import *
    from PyQt6.QtQml import *
    from PyQt6.QtPrintSupport import *
    from PyQt6.QtPositioning import *
    from PyQt6.QtOpenGL import *
    from PyQt6.QtNfc import *
    from PyQt6.QtMultimediaWidgets import *
    from PyQt6.QtHelp import *
    from PyQt6.QtDesigner import *
    from PyQt6.QtDBus import *
    from PyQt6.QtBluetooth import *


    from PyQt6 import (
        QtGui, 
        QtWidgets, 
        QtCore, 
        QtMultimedia, 
        QtNetwork, 
        QtWebEngineWidgets, 
        QtWebEngineCore, 
        QtXml, 
        QtWebSockets, 
        QtWebChannel,
        QtTextToSpeech,
        QtDesigner,
        QtHelp,
        QtDBus,
        QtBluetooth,
        QtOpenGL,
        QtNfc,
        QtMultimediaWidgets,
        QtPositioning,
        QtPrintSupport,
        QtQml,
        QtQuick3D,
        QtQuickWidgets,
        QtQuick,
        QtRemoteObjects,
        QtSensors,
        QtSerialPort,
        QtTest,
        QtSql,
        QtSvg
    )

    qModules = (
        QtGui, 
        QtWidgets, 
        QtCore, 
        QtMultimedia, 
        QtNetwork, 
        QtWebEngineWidgets, 
        QtWebEngineCore, 
        QtXml, 
        QtWebSockets, 
        QtWebChannel,
        QtTextToSpeech,
        QtDesigner,
        QtHelp,
        QtDBus,
        QtBluetooth,
        QtOpenGL,
        QtNfc,
        QtMultimediaWidgets,
        QtPositioning,
        QtPrintSupport,
        QtQml,
        QtQuick3D,
        QtQuickWidgets,
        QtQuick,
        QtRemoteObjects,
        QtSensors,
        QtSerialPort,
        QtTest,
        QtSql,
        QtSvg
    )

    classes_to_import:list[str] = []

    for k, v in list(globals().items()):
        if k.startswith('Q'):
            classes_to_import.append(k)
            print(k)

    print(classes_to_import)

    text = f"""from PyQt6 import (
    QtGui, 
    QtWidgets, 
    QtCore, 
    QtMultimedia, 
    QtNetwork, 
    QtWebEngineWidgets, 
    QtWebEngineCore, 
    QtXml, 
    QtWebSockets, 
    QtWebChannel,
    QtTextToSpeech,
    QtDesigner,
    QtHelp,
    QtDBus,
    QtBluetooth,
    QtOpenGL,
    QtNfc,
    QtMultimediaWidgets,
    QtPositioning,
    QtPrintSupport,
    QtQml,
    QtQuick3D,
    QtQuickWidgets,
    QtQuick,
    QtRemoteObjects,
    QtSensors,
    QtSerialPort,
    QtTest,
    QtSql,
    QtSvg
)

from stdqt6._all import (
    {',\n    '.join(classes_to_import)}
)"""

    with open('./stdqt6/__init__.py', 'w', encoding='utf-8') as f:
        f.write(text)