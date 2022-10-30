import string
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, update
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
import requests
import xml.etree.ElementTree as ET
import urllib.parse

@dataclass
class db_update:
    name: string
    bgg_id: string
    description: string
    thumbnail: string
    image: string

def main():
    meta = MetaData()

    game = Table(
        'game', meta, 
        Column('game_id', UUID, primary_key = True), 
        Column('name', String), 
        Column('description', Text), 
        Column('image', String),
        Column('thumbnail', String),
        Column('min_players', Integer),
        Column('max_players', Integer),
        Column('duration_upper', Integer),
        Column('duration_lower', Integer),
        Column('owner_id', UUID, ForeignKey('owner.owner_id')), 
        Column('reference', String),
        Column('bgg_id', String),
    )

    selection = game.select()

    game_names = []
    engine = create_engine("postgresql://DHubbert:v2_3v23f_Vn2GL8HQscmQmLHQdHFMRzA@db.bit.io/DHubbert/BoardGames", echo=True)
    conn = engine.connect()
    for row in conn.execute(selection):
        game_names.append(row['name'])
    conn.close()
    engine.dispose()

    db_updates = []
    for game_name in game_names:
        query=f'https://boardgamegeek.com/xmlapi/search?search={urllib.parse.quote_plus(game_name)}'
#        print(query)
        response = requests.get(query)
    #            print(response.content)
        root = ET.fromstring(response.content)
        match_found=False
        for boardgame in root:
            boardgame_name = boardgame.find('./name').text
            if boardgame_name == game_name:
                match_found=True
                bgg_id=boardgame.attrib['objectid']
                game_query=f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}'
                game_response=requests.get(game_query)
                print(f'Found {game_name} with id {bgg_id}')
                game_root = ET.fromstring(game_response.content)
                thumbnailNode = game_root.find('./item/thumbnail')
                if thumbnailNode is not None:
                    thumbnail=thumbnailNode.text
                else:
                    thumbnail=''
                imageNode = game_root.find('./item/image')
                if imageNode is not None:
                    image=imageNode.text
                else:
                    image=''
                descriptionNode = game_root.find('./item/description')
                if descriptionNode is not None:
                    description=descriptionNode.text
                db_updates.append(db_update(game_name, bgg_id, description, thumbnail, image)) 
#                print(game_response.content)
        if match_found==False:
            print(f'No match found for {game_name}')

    print('')
    print('Matching finished, moving to updates.')
    print('')

    engine = create_engine("postgresql://DHubbert:v2_3v23f_Vn2GL8HQscmQmLHQdHFMRzA@db.bit.io/DHubbert/BoardGames", echo=True)
    for game_update in db_updates:
        conn = engine.connect()
        print(f'Updating {game_update.name}')
        update_query = (update(game).where(game.c.name == game_update.name).values(bgg_id=game_update.bgg_id, description=game_update.description, thumbnail=game_update.thumbnail, image=game_update.image))
        print('')
        print(update_query)
        print('')
        conn.execute(update_query)
        conn.close()
    engine.dispose()
    print('Done')


if __name__ == '__main__':
    main()