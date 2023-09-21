import json
import os
import shutil
import sys
import unittest
from pathlib import Path

import yahtzee


class YathzeeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        proof_path = Path(f'{os.getcwd()}').joinpath('test_data', 'proof')
        if proof_path.exists():
            shutil.rmtree(proof_path)

    def test_exit_if_no_args(self):
        sys.argv = ['yahtzee']
        with self.assertRaises(SystemExit):
            yahtzee.main()

    def test_detect_dice_in_images(self):
        images = [
            ['blurry.jpg', [2, 3, 6, 6, 6]],
            ['test_full.jpg', [2, 3, 6, 6, 6]],
            ['test_full2.jpg', [1, 1, 4, 5, 6]],
            ['test_full4.jpg', [2, 3, 5, 6, 6]],
            ['241fed8b-9a3d-4a5e-9dbd-b21ddb064d72.jpg', [1, 2, 4, 5, 6]],
            ['26d741af-a1c1-45cd-b1bd-f72252f0e86f.jpg', [1, 3, 3, 4, 4]],
            ['367cb5a5-44ae-4b40-bfbb-2cb95b91533b.jpg', [2, 3, 4, 5, 6]],
            ['bd975686-5830-41c6-9af3-4cbb883066e2.jpg', [1, 1, 3, 5, 6]],
            ['daf0add8-b70a-4660-ad62-d43db93c8db0.jpg', [3, 4, 6, 6, 6]],
            ['e9bf8366-83c8-4332-8803-41fffb9b9d85.jpg', [1, 2, 3, 4, 6]],
        ]

        for image in images:
            sys.argv = ['yahtzee', f'test_data/{image[0]}']
            self.assertEqual(sorted(yahtzee.main()), image[1], msg=f'Different dice found for {image[0]}')

    def test_cannot_detect_dice_in_unclear(self):
        images = [
            '70140841-bf2f-4817-994d-ba46014ff317.jpg',
            '7517023f-7c60-42a2-945b-0d087ed4009c.jpg',
            '9de77830-8966-4383-b738-068881c6d4be.jpg',
            'ba09b75a-b843-4332-bb9b-99fac27eac79.jpg',
            'c1c50a07-be3b-450a-bcb5-8705c62f98a6.jpg',
            'e2e90d08-9162-4594-872f-e8e88fbe7cfa.jpg',
            'skewed.jpg',
        ]
        with self.assertRaises(SystemExit):
            for i in images:
                sys.argv = ['yahtzee', f'test_data/{i}']
            yahtzee.main()


if __name__ == '__main__':
    unittest.main()
