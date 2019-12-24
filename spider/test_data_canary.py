from unittest import TestCase

from allclasses import ClassesSpider
from converter import Converter
import json


# Run some tests on crawled data
class TestDataCanary(TestCase):
    def test_wiki_links(self):
        data = Converter.get_data()
        wiki_links = [x for x in data if x['type'] == ClassesSpider.TYPE_WIKI_LINK_PROFESSOR]
        profs_with_links = {x['instructor']: x for x in wiki_links if 'wiki_title' in x}
        # assert len(profs_with_links) == len(set(profs_with_links))
        profs_with_links = profs_with_links
        check_set = set(['Michael Doyle', 'Kenneth Shepard', 'Rebecca Young', 'Kenneth Jackson', 'Obery Hendricks', 'Van Mow', 'Jennifer Lee', 'Jonathan David', 'Frank Guridy', 'Paul Richards', 'Philip White', 'Xi Chen', 'Feng Li', 'Jack Norton', 'Richard Friesner', 'Brent Edwards', 'Kathleen Taylor', 'George Lewis', 'Duong Phong', 'Donald Ferguson', 'Chong Li', 'Alice Brown', 'Zhi Li', 'Giovanni Giorgini', 'Sunil Agrawal', 'Richard Osgood', 'Ying Qian', 'Robert Wolff', 'John Marshall', 'Elke Weber', 'Achille Varzi', 'Jean Cohen', 'Luis Campos', 'Wei Shang', 'Souleymane Diagne', 'Richard Friedman', 'Michael Harris', 'Yang An', 'Joseph Fasano', 'Shane McCrae', 'Margo Jefferson', 'Marie Lee', 'Heidi Julavits', 'William Hill', 'Marianne Hirsch', 'Janet Jakobsen', 'Saidiya Hartman', 'Alice Reagan', 'Andrew Gelman', 'Michael Sobel', 'Zhiliang Ying', 'Bruno Bosteels', 'Shamus Khan', 'Peter Bearman', 'Yinon Cohen', 'Todd Gitlin', 'Saskia Sassen', 'Gary Dorrien', 'Elizabeth Castelli', 'Bernard Faure', 'Robert Somerville', 'Mark Taylor', 'Sarah Woolley', 'Carl Hart', 'Tory Higgins', 'Sheena Iyengar', 'Ursula Staudinger', 'Yaakov Stern', 'Norma Graham', 'Robert Remez', 'Ira Katznelson', 'Jack Snyder', 'Richard Betts', 'Richard Clark', 'Paula Franzese', 'Lee Bollinger', 'Kimberly Marten', 'Robert Jervis', 'Boris Altshuler', 'Erick Weinberg', 'Charles Hailey', 'Malvin Ruderman', 'Norman Christ', 'William Zajc', 'Elena Aprile', 'Alfred Mueller', 'Rachel Rosen', 'Brian Greene', 'Frederick Neuhouser', 'David Albert', 'Philip Kitcher', 'Patricia Kitcher', 'Jenann Ismael', 'Lydia Goehr', 'Michele Moody-Adams', 'Haim Gaifman', 'Axel Honneth', 'Christopher Peacocke', 'Christia Mercer', 'Akeel Bilgrami', 'Taylor Carman', 'Caroline Nichols', 'Brett Boretti', 'Kevin Anderson', 'Scott Donie', 'Jeffrey Milarsky', 'Aaron Fox', 'Georg Friedrich Haas', 'Elaine Sisman', 'Oliver Jovanovic', 'Vincent Racaniello', 'Hod Lipson', 'Y. Lawrence Yao', 'Khatchig Mouradian', 'Timothy Mitchell', 'Wael Hallaq', 'Joseph Massad', 'Sudipta Kaviraj', 'Aftab Ahmad', 'Simon Brendle', 'Chiu-Chu Liu', 'Andrei Okounkov', 'Aise Johan de Jong', 'Ivan Corwin', 'Daniela De Silva', 'Panagiota Daskalopoulos', 'Dorian Goldfeld', 'Mu-Tao Wang', 'Peter Woit', 'Haruo Shirane', 'Teodolinda Barolini', 'Ward Whitt', 'Donald Goldfarb', 'Emanuel Derman', 'Awi Federgruen', 'Sheldon Weinig', 'Taylor Brook', 'Matthew Ricketts', 'Mamadou Diouf', 'Madeleine Zelin', 'Jo Becker', 'Andrew Nathan', 'Manan Ahmed', 'Susan Pedersen', 'Mae Ngai', 'Barbara Fields', 'Elisheva Carlebach', 'Rashid Khalidi', 'Michael Stanislawski', 'George Chauncey', 'Stephanie McCurry', 'Matthew Connelly', 'Richard Billows', 'Antoine Compagnon', 'Noni Carter', 'Lance Weiler', 'Caryn James', 'James Schamus', 'Annette Insdorf', 'Austin Quigley', 'Jacob Fish', 'John McWhorter', 'Edward Mendelson', 'Nellie Hermann', 'Jenny Davidson', 'Debasis Mitra', 'Michal Lipson', 'Yannis Tsividis', 'Xiaodong Wang', 'Maureen Raymo', 'Terry Plank', 'Ruth DeFries', 'Steven Goldstein', 'Arlene Fiore', 'Paul Olsen', 'Jonah Rockoff', 'Stephanie Schmitt-Grohe', 'Andrea Prat', 'Edmund Phelps', 'Joseph Stiglitz', 'Michael Woodford', 'Graciela Chichilnisky', 'Serena Ng', 'Harrison Hong', 'Sunil Gulati', 'Clifford Stein', 'Deborah Paredez', 'Nathalie Handal', 'Eric Gamalinda', 'Sayantani DasGupta', 'Hisham Matar', 'Xiaolu Guo', 'Christos Papadimitriou', 'Jeannette Wing', 'Vishal Misra', 'Julia Hirschberg', 'Steven Bellovin', 'Salvatore Stolfo', 'Bjarne Stroustrup', 'Michael Collins', 'Kathleen McKeown', 'Brian Smith', 'Jason Nieh', 'Roxana Geambasu', 'Ronald Baecker', 'Stefan Andriopoulos', 'Helene Foley', 'Orhan Pamuk', 'Theodore Zoli', 'Jingguang Chen', 'James Leighton', 'Gerard Parkin', 'Gordana Vunjak-Novakovic', 'Tal Danino', 'Elizabeth Hillman', 'Andrew Laine', 'Michael Sheetz', 'Martin Chalfie', 'Deborah Mowshowitz', 'Carol Friedman', 'Caleb Scharf', 'David Helfand', 'Qiang Du', 'Adam Sobel', 'Mark Cane', 'Renata Wentzcovitch', 'Allen Boozer', 'Elizabeth Povinelli', 'Claudio Lomnitz', 'Ralph Holloway', 'Partha Chatterjee', 'Lila Abu-Lughod', 'Michael Taussig', 'Marilyn Ivy', 'John Pemberton', 'Mahmood Mamdani', 'Seth Schwartz', 'Jeremy Dauber', 'Robert Pollack', 'Vidya Dehejia', 'Branden Joseph', 'Rosalyn Deutsche', 'Barry Bergdoll', 'Farah Griffin', 'Robert Gooding-Williams'])

        # checks
        diff1 = check_set.difference(profs_with_links.keys())
        print("Those professors are in check set, but were not linked to Wikipedia:")
        print(diff1)

        diff2 = set(profs_with_links.keys()).difference(check_set)
        print("Those professors were linked, but are not in check set for Wikipedia:")
        print(diff2)
        self.print_prof_links(diff2, profs_with_links)
        assert len(diff1) == 0 and len(diff2) == 0

    def print_prof_links(self, profs, profs_with_links):
        for prof in profs:
            print(prof + " linked to: " + profs_with_links[prof]['wiki_title'])
