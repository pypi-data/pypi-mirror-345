from src.pytwincatparser.Twincat4024Strategy import Twincat4024Strategy
from pathlib import Path   


strategy = Twincat4024Strategy()

    #print(strategy.load_objects(Path("TwincatFiles\Base\FB_Base.TcPOU")))
    #print(strategy.load_objects(Path("TwincatFiles\Commands\ST_PmlCommand.TcDUT")))
    #print(strategy.load_objects(Path("TwincatFiles\TwincatPlcProject.plcproj")))
for obj in strategy.load_objects(Path("TwincatFiles\moreFiles\Main.plcproj")):
    print(f"name:{obj.name} namespace:{obj.name_space}, parent:{obj.parent.name if obj.parent is not None else ""}, ident: {obj.get_identifier()}")