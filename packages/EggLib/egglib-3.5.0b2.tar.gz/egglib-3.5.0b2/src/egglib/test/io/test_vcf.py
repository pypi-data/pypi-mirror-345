"""
    Copyright 2024-2025 Thomas Coudoux, Stéphane De Mita, Mathieu Siol

    This file is part of EggLib.

    EggLib is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EggLib is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with EggLib.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest, egglib, pathlib, tempfile, os, shutil, subprocess, collections, re
path = pathlib.Path(__file__).parent / '..' / 'data'

#  helper code to create a temporary BCF and its header
class TempfileHelper:
    def __init__(self, vcf_data):
        fh = tempfile.NamedTemporaryFile(delete=False)
        fh.close()
        self.bcf = pathlib.Path(fh.name)

        fh = tempfile.NamedTemporaryFile(delete=False)
        fh.close()
        self.idx = pathlib.Path(fh.name)

        subprocess.run(["bcftools", "view", '-o', self.bcf, '-O', 'b', '-'], input=vcf_data, encoding='utf8')
        egglib.io.index_vcf(self.bcf, self.idx)

    def close(self):
        self.bcf.unlink(missing_ok=True)
        self.idx.unlink(missing_ok=True)

    def __del__(self):
        self.close()

class VCF_test(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.d.name)
        self.idx = None

    def tearDown(self):
        del self.d
        if self.idx is not None: self.idx.unlink(missing_ok=True)

    def test_fname(self):
        egglib.io.VCF(str(path / 'b.vcf')) # RuntimeError if htslib is off
        egglib.io.VCF(str(path / 'b.bcf'))
        egglib.io.VCF(path / 'b.bcf') # support for Path objects
        with self.assertRaisesRegex(TypeError, 'not list$'):
            egglib.io.VCF([path / 'b.bcf'])
        with self.assertRaisesRegex(TypeError, 'not int$'):
            egglib.io.VCF(404)
        with self.assertRaisesRegex(OSError, 'cannot open file: .+not\.exist'):
            egglib.io.VCF(path / 'not.exist')
        with self.assertRaisesRegex(ValueError, 'invalid file: .+b\.gff3'):
            egglib.io.VCF(path / 'b.gff3')

    def test_index_default(self): # (only supported on BCF)
        shutil.copyfile(path / 'b.bcf', self.path / 'b.bcf')
        vcf = egglib.io.VCF(self.path / 'b.bcf')
        self.assertFalse(vcf.has_index)
        egglib.io.index_vcf(self.path / 'b.bcf')
        vcf = egglib.io.VCF(self.path / 'b.bcf')
        self.assertTrue(vcf.has_index)

    def test_index_custom(self):
        shutil.copyfile(path / 'b.bcf', self.path / 'b.bcf')
        vcf = egglib.io.VCF(self.path / 'b.bcf')
        self.assertFalse(vcf.has_index)
        egglib.io.index_vcf(self.path / 'b.bcf', self.path / 'index')
        vcf = egglib.io.VCF(self.path / 'b.bcf')
        self.assertFalse(vcf.has_index)
        vcf = egglib.io.VCF(self.path / 'b.bcf', index=self.path / 'index')
        self.assertTrue(vcf.has_index)

    def test_ctor_args(self):
        with self.assertRaisesRegex(ValueError, 'cannot import index from: .+not\.exist'):
            egglib.io.VCF(fname=path / 'b.bcf',
                          index=path / 'not.exist')

        self.assertTrue((path / 'b.gff3').is_file())
        with self.assertRaisesRegex(ValueError, 'cannot import index from: .+b\.gff3'):
            egglib.io.VCF(fname=path / 'b.bcf',
                          index=path / 'b.gff3')

        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')
            self.assertEqual(vcf.num_samples, 4)
            self.assertEqual(vcf.get_samples(), ['INDIV1', 'INDIV2', 'INDIV3', 'INDIV4'])

        vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=['INDIV1', 'INDIV3', 'INDIV2', 'INDIV4'])
        self.assertEqual(vcf.num_samples, 4)
        self.assertEqual(vcf.get_samples(), ['INDIV1', 'INDIV2', 'INDIV3', 'INDIV4'])

        vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=['INDIV2', 'INDIV1', 'INDIV1', 'INDIV4'])
        self.assertEqual(vcf.num_samples, 3)
        self.assertEqual(vcf.get_samples(), ['INDIV1', 'INDIV2', 'INDIV4'])

        vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=['INDIV2', 'INDIV4'])
        self.assertEqual(vcf.num_samples, 2)
        self.assertEqual(vcf.get_samples(), ['INDIV2', 'INDIV4'])

        vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=[])
        self.assertEqual(vcf.num_samples, 0)
        self.assertEqual(vcf.get_samples(), [])

        with self.assertRaisesRegex(ValueError, 'unknown sample at position 5'):
            vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=['INDIV1', 'INDIV2', 'INDIV3', 'INDIV4', 'INDIV5'])

        with self.assertRaisesRegex(TypeError, 'subset: expect a sequence of strings'):
            vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=1)

        with self.assertRaisesRegex(TypeError, 'subset: expect a sequence of strings'):
            vcf = egglib.io.VCF(fname=path / 'b.bcf', subset=['INDIV1', 1])

    def test_samples(self):
        vcf = egglib.io.VCF(fname=path / 'b.bcf')
        self.assertEqual([vcf.get_sample(i) for i in range(4)], ['INDIV1', 'INDIV2', 'INDIV3', 'INDIV4'])
        with self.assertRaisesRegex(IndexError, 'sample index out of range'):
            vcf.get_sample(4)

    def test_defaults(self):
        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')
            self.assertIsNone(vcf.get_id())
            self.assertIsNone(vcf.get_alleles())
            self.assertIsNone(vcf.get_alternate())
            self.assertIsNone(vcf.get_chrom())
            self.assertIsNone(vcf.get_filter())
            self.assertIsNone(vcf.get_formats())
            self.assertIsNone(vcf.get_genotypes())
            self.assertIsNone(vcf.get_infos())
            self.assertIsNone(vcf.get_phased())
            self.assertIsNone(vcf.get_pos())
            self.assertIsNone(vcf.get_quality())
            self.assertIsNone(vcf.get_reference())
            self.assertIsNone(vcf.get_types())
            self.assertFalse(vcf.is_snp())
            self.assertIsNone(vcf.get_errors())
            self.assertIsNone(vcf.get_info('NO.SUCH.TAG'))
            self.assertIsNone(vcf.get_format('NO.SUCH.TAG', 0))

    def compare_values(self, ctrl, v1, v2, idx, k):
        if isinstance(ctrl, list):
            self.assertEqual(len(ctrl), len(v1), msg=f'site index: {idx+1} - {k}')
            self.assertEqual(len(ctrl), len(v2), msg=f'site index: {idx+1} - {k}')
            for i in range(len(ctrl)):
                self.compare_values_i(ctrl[i], v1[i], v2[i], idx, k, tag=f' item #{i+1}')
        else:
            self.compare_values_i(ctrl, v1, v2, idx, k, tag='')

    def compare_values_i(self, ctrl, v1, v2, idx, k, tag):
        if ctrl is None:
            self.assertIsNone(v1, msg=f'site index: {idx+1} - {k}{tag}')
            self.assertIsNone(v2, msg=f'site index: {idx+1} - {k}{tag}')
        elif isinstance(ctrl, float):
            self.assertAlmostEqual(ctrl, v1, msg=f'site index: {idx+1} - {k}', places=6)
            self.assertAlmostEqual(ctrl, v2, msg=f'site index: {idx+1} - {k}', places=6)
        else:
            self.assertEqual(ctrl, v1, msg=f'site index: {idx+1} - {k}')
            self.assertEqual(ctrl, v2, msg=f'site index: {idx+1} - {k}')

    def test_get_info(self):
        ref_infos = [
            {'DP': 100, 'V': [4], 'W': [41, None], 'AA': 'AA', 'BIDON': 'G',
             'ALT':['.'], 'X': 0.2, 'Y': [1.2], 'GOOD': True, 'INT': None},
            {'AA': 'A', 'TRUC': [407, 12]},
            {'AA': 'C', 'P': [4.13]},
            {'AA': 'C', 'ALT': 'G,C'}, # strings can not represented as multiple values
            {'AA': 'G', 'P': [5.3, None, 3.001]},
            {'AA': 'G', 'TRUC': [None, 500400300]},
            {'AA': 'G', 'DP': None},
            {'AA': 'C', 'ALT': '.'}, # string missing values are not recognized
            {'AA': 'CTC', 'TRUC': [20, None]},
            {'AA': 'A', 'TRI': [1, 2], 'ALT': 'C,G,T', 'GOOD': True},
            {'AA': 'A', 'ALT': '.'}
        ]

        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')

            for idx, ref in enumerate(ref_infos):
                self.assertTrue(vcf.read(), msg=f'site index: {idx+1}')
                infos = vcf.get_infos()
                self.assertEqual(infos.keys(), ref.keys(), msg=f'site index: {idx+1}')
                with self.assertRaisesRegex(ValueError, 'invalid info key: NOT.EXIST'):
                    vcf.get_info('NOT.EXIST')
                for k, ctrl in ref.items():
                    v1 = infos[k]
                    v2 = vcf.get_info(k)
                    self.compare_values(ctrl, v1, v2, idx, k)
            self.assertFalse(vcf.read())

    def test_get_format(self):
        ref_format = [
            {},
            {'TEST1': [None, 1, None, None]},
            {'TEST2': [[1, 2], [1, None], [None], [1]]},
            {'TEST3': [0.1, 0.2, None, 0.4]},
            {'TEST4': [[None], [0.2], [0.1, 0.2, 0.3, 0.1], [6]]},
            {'TEST5': ['hipidop', 'a string', 'hap', 'hipidop']},
            {},
            {},
            {},
            {'TEST5': ['.', 'nothing', 'not more', 'something!'],
             'TEST1': [702, 703, 704, 705]},
            {}
        ]

        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')

            for idx, ref in enumerate(ref_format):
                self.assertTrue(vcf.read(), msg=f'site index: {idx+1}')
                fmts = vcf.get_formats()
                self.assertIsInstance(fmts, list, msg=f'site index: {idx+1}')
                self.assertEqual(len(fmts), 4, msg=f'site index: {idx+1}')
                for idv, fmt in enumerate(fmts):
                    self.assertEqual(fmt.keys(), ref.keys(), msg=f'site index: {idx+1}')
                    for key, ctrl in ref.items():
                        self.compare_values(ctrl[idv], fmt[key], vcf.get_format(key, idv), idx, key)

                with self.assertRaisesRegex(ValueError, 'invalid format key: NOT.EXIST'):
                    vcf.get_format('NOT.EXIST', 0)
                if len(ref) > 0:
                    with self.assertRaisesRegex(IndexError, 'sample index out of range'):
                        vcf.get_format(list(ref)[0], 4)
                    self.assertEqual(vcf.get_format(list(ref)[0], -1),
                                     vcf.get_format(list(ref)[0], 3))
                    self.assertEqual(vcf.get_format(list(ref)[0], -2),
                                     vcf.get_format(list(ref)[0], 2))
                    self.assertEqual(vcf.get_format(list(ref)[0], -3),
                                     vcf.get_format(list(ref)[0], 1))
                    self.assertEqual(vcf.get_format(list(ref)[0], -4),
                                     vcf.get_format(list(ref)[0], 0))
                    with self.assertRaisesRegex(IndexError, 'sample index out of range'):
                        vcf.get_format(list(ref)[0], -5)

            self.assertFalse(vcf.read())

    def test_error(self):
        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')
            while vcf.read():
                self.assertEqual(vcf.get_errors(), [])

        s = ('##fileformat=VCFv4.2\n'
             '##contig=<ID=ctg1,len=1000>\n'
             '##INFO=<ID=FLOAT,Number=1,Type=Float,Description="Something">\n'
             '##FORMAT=<ID=INT,Number=1,Type=Integer,Description="Something else">\n'
             '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n'
             'ctg1	10	.	A	.	.	PASS	FLOAT=1	INT	1	2	3	4\n'
             'ctg1	20	.	A	.	.	PASS	FLOAT=1.1;DOUBLE=4.5	INT	1	2	3	4\n'
             'ctg1	30	.	A	.	.	PASS	FLOAT=1.1	INT	1	2	XXX	4\n'
             'ctg1	40	.	A	.	.	PASS	FLOAT=1.5	INT	1	2	3	4\n')

        with open(self.path / 'tmp.vcf', 'w') as f:
            f.write(s)

        vcf = egglib.io.VCF(fname=self.path / 'tmp.vcf')
        self.assertTrue(vcf.read())
        self.assertEqual(vcf.get_errors(), [])
        self.assertTrue(vcf.read())
        self.assertGreater(len(vcf.get_errors()), 0)
        with self.assertRaisesRegex(ValueError, 'critical error while reading a variant'):
            vcf.read()
        self.assertTrue(vcf.read())
        self.assertEqual(vcf.get_errors(), [])
        self.assertFalse(vcf.read())

    def helper_test_goto(self, vcf:egglib.io.VCF,
                ctg:str, pos:int = None, limit:str = None,
                expected_ctg_error:bool = False,
                expected_pos_error:bool = False,
                expected_position:int = None):
        if expected_ctg_error:
            with self.assertRaisesRegex(ValueError, f'unknown target name: {ctg}'):
                if pos is None: vcf.goto(ctg)
                elif limit is None: vcf.goto(ctg, pos)
                else: vcf.goto(ctg, pos, limit)
            return
        if pos is None: res = vcf.goto(ctg)
        elif limit is None: res = vcf.goto(ctg, pos)
        else: res = vcf.goto(ctg, pos, limit)
        if expected_pos_error:
            self.assertFalse(res)
            self.assertIsNone(vcf.get_chrom())
            self.assertIsNone(vcf.get_pos())
        else:
            self.assertTrue(res)
            self.assertEqual(vcf.get_chrom(), ctg)
            if expected_position is None and pos is not None:
                expected_position = pos
            if expected_position is not None:
                self.assertEqual(vcf.get_pos(), expected_position)

    def test_goto(self):
        # load without index
        vcf = egglib.io.VCF(fname=path / 'b.bcf')
        with self.assertRaisesRegex(ValueError, 'an index is required'):
            vcf.goto('ctg2')

        # create index and load
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        self.idx = pathlib.Path(f.name)
        egglib.io.index_vcf(path / 'b.bcf', self.idx)
        vcf = egglib.io.VCF(fname=path / 'b.bcf', index=self.idx)
        self.assertTrue(vcf.has_index)

        # go to a contig
        self.helper_test_goto(vcf, 'ctg2', expected_position=1014)

        # next pos
        self.assertTrue(vcf.read())
        self.assertEqual(vcf.get_chrom(), 'ctg2')
        self.assertEqual(vcf.get_pos(), 1015)

        # go to a position
        self.helper_test_goto(vcf, 'ctg2', 1049)

        # go to an invalid contig
        self.helper_test_goto(vcf, 'ctgN', expected_ctg_error=True)

        # go back near beginning
        self.helper_test_goto(vcf, 'ctg1', 1000)

        # reopen and go to first position of first contig
        vcf = egglib.io.VCF(fname=path / 'b.bcf', index=self.idx)
        self.helper_test_goto(vcf, 'ctg1', expected_position=999)

        # go to a non-existing position and fix with limit
        self.helper_test_goto(vcf, 'ctg2', 1017, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg2', 1017, limit=1019, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg2', 1017, limit=1020, expected_position=1019)
        self.helper_test_goto(vcf, 'ctg3', 1067, limit=egglib.io.VCF.END, expected_position=1099)

        with self.assertRaisesRegex(ValueError, '`limit` must be larger than `pos`'):
            self.helper_test_goto(vcf, 'ctg2', 1019, limit=1019)
        with self.assertRaises(TypeError):
            self.helper_test_goto(vcf, 'ctg2', 1019, limit='END')
        with self.assertRaisesRegex(ValueError, '`limit` must be strictly positive'):
            self.helper_test_goto(vcf, 'ctg2', 1019, limit=-10)

        # another test
        self.helper_test_goto(vcf, 'ctg2', 1017, limit=egglib.io.VCF.END, expected_position=1019)

        # go past the end of a contig
        self.helper_test_goto(vcf, 'ctg2', 1200, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg2', 1200, limit=1300, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg2', 1200, limit=egglib.io.VCF.END, expected_pos_error=True)
        self.assertEqual(vcf.get_info(), None)

        # go back to actual beginning
        self.helper_test_goto(vcf, 'ctg1', expected_position=999)

        # go past the end of the file
        self.helper_test_goto(vcf, 'ctg3', 9999, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg3', 9999, limit=10000, expected_pos_error=True)
        self.helper_test_goto(vcf, 'ctg3', 9999, limit=egglib.io.VCF.END, expected_pos_error=True)
        self.assertEqual(vcf.get_info(), None)
        
    def test_dump(self):
        header = """##fileformat=VCFv4.1
##FILTER=<ID=PASS,Description="All filters passed">
##contig=<ID=ctg1,len=1500>
##contig=<ID=ctg2,len=1500>
##contig=<ID=ctg3,len=1500>
##ALT=<ID=DEL,Description="Deletion">
##INFO=<ID=AA,Number=1,Type=String,Description="Ancestral allele">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Depth">
##INFO=<ID=V,Number=A,Type=Integer,Description="Whatever">
##INFO=<ID=W,Number=.,Type=Integer,Description="Whatever">
##INFO=<ID=X,Number=1,Type=Float,Description="Something">
##INFO=<ID=Y,Number=.,Type=Float,Description="Something else">
##INFO=<ID=BIDON,Number=1,Type=String,Description="Bidon">
##INFO=<ID=TRUC,Number=2,Type=Integer,Description="Something">
##INFO=<ID=P,Number=.,Type=Float,Description="Value">
##INFO=<ID=ALT,Number=A,Type=String,Description="First base of each alternate allele (note: htslib ignores number of type String: always one)">
##INFO=<ID=INT,Number=1,Type=Integer,Description="An integer">
##INFO=<ID=TRI,Number=3,Type=Float,Description="Three values">
##INFO=<ID=GOOD,Number=0,Type=Flag,Description="Flag">
##INFO=<ID=NOTGOOD,Number=0,Type=Flag,Description="A similar flag">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=TEST1,Number=1,Type=Integer,Description="Test 1">
##FORMAT=<ID=TEST2,Number=2,Type=Integer,Description="Test 2">
##FORMAT=<ID=TEST3,Number=1,Type=Float,Description="Test 3">
##FORMAT=<ID=TEST4,Number=4,Type=Float,Description="Test 4">
##FORMAT=<ID=TEST5,Number=1,Type=String,Description="Test 5">
##FILTER=<ID=triple,Description="three alleles">
##FILTER=<ID=multi,Description="different types of alleles">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4
"""

        lines = [
            "ctg1	1000	snp1;first;zero	A	T	4	PASS	DP=100;V=4;W=41,.;INT=.;AA=AA;BIDON=G;ALT=.;X=0.2;Y=1.2;GOOD	GT	0|0	0|1	0|0	1|1\n",
            "ctg1	1001	snp11	A	AA	.	PASS	AA=A;TRUC=407,12	TEST1:GT	.:0|0	1:0|1	.:0|0	.:1|1\n",
            "ctg1	1010	snp2	C	G,T	.	triple	AA=C;P=4.13	GT:TEST2	1|1:1,2	0|1:1,.	1|0:.	2|2:1\n",
            "ctg1	1011	snp21	C	G,CTT	.	triple;multi	AA=C;ALT=G,C	GT:TEST3	1|1:0.1	0|1:0.2	1|0:.	2|2:0.4\n",
            "ctg2	1015	.	G	TAA	.	PASS	AA=G;P=5.3,.,3.001	GT:TEST4	0|1:.	1|1:0.2	0|0:0.1,0.2,0.3,0.1	0|0:6\n",
            "ctg2	1016	snp201;snp+	G	GAA	.	PASS	AA=G;TRUC=.,500400300	GT:TEST5	0|1:hipidop	1|1:a string	0|0:hap	0|0:hipidop\n",
            "ctg2	1020	snp3;snp3	G	T	.	PASS	AA=G;DP=.	GT	0|0	0|1	0|0	1|1\n",
            "ctg2	1030	snp4	C	A	.	PASS	AA=C;ALT=.	GT	0|0	0|1	0|0	1|1\n",
            "ctg2	1050	snp5	CTC	ATG	.	PASS	AA=CTC;TRUC=20,.	GT	0|0	0|1	.	1|1\n",
            "ctg3	1060	no_snp	A	C	.	PASS	AA=A;TRI=1,2;ALT=C,G,T;GOOD	TEST5:GT:TEST1	.:0|0|0:702	nothing:0|0/0:703	not more:0/0/1:704	something!:0/1/1:705\n",
            "ctg3	1100	.	A	.	.	PASS	AA=A;ALT=.	GT	0|0	0|.	./.	.|.\n"
        ]

        # constructor errors
        with self.assertRaisesRegex(ValueError,'dump file cannot have the same name as: {}'.format(path / 'b.vcf')):
            vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=path / 'b.vcf')
        for fname in [ path / '.vcf', path / '.bcf',
                       path / '.vcf.gz', path / '.vgf',
                       '.vcf', 'a.vc', '.gz', '.vcf.gz', 'a.truc']:
            with self.assertRaisesRegex(ValueError, 'invalid dump file name'):
                vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=fname)

        # initialization of file (export header)
        vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=self.path / 'test.vcf')
        del vcf
        with open(self.path / 'test.vcf') as f:
            self.assertEqual(f.read(), header)

        # export full file
        vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=self.path / 'test.vcf')
        while vcf.read():
            vcf.dump_record()
        vcf.dump_close()
        with open(self.path / 'test.vcf') as f:
            self.assertEqual(f.read(), header + ''.join(lines))

        # export file skipping every 2nd line
        vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=self.path / 'test.vcf')
        while vcf.read():
            vcf.dump_record()
            vcf.read()
        vcf.dump_close()
        with open(self.path / 'test.vcf') as f:
            self.assertEqual(f.read(), header + ''.join(lines[::2]))

        # export only fifth line
        vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=self.path / 'test.vcf')
        for i in range(4): vcf.read()
        vcf.read()
        vcf.dump_record()
        vcf.dump_close()
        with open(self.path / 'test.vcf') as f:
            self.assertEqual(f.read(), header + lines[4])

        # effect of subset
        vcf = egglib.io.VCF(path / 'b.vcf', dumpfile=self.path / 'test.vcf',
                subset = ['INDIV1', 'INDIV3'])
        vcf.dump_close()
        vcf = egglib.io.VCF(self.path / 'test.vcf')
        self.assertEqual(vcf.get_samples(), ['INDIV1', 'INDIV3'])

        # errors
        vcf = egglib.io.VCF(path / 'b.vcf')
        with self.assertRaisesRegex(ValueError, 'no record available'):
            vcf.dump_record()
        vcf.read()
        with self.assertRaisesRegex(ValueError, 'no dump file open'):
            vcf.dump_record()
        with self.assertRaisesRegex(ValueError, 'no dump file open'):
            vcf.dump_close()

    def test_as_site(self):
        vcf = egglib.io.VCF(path / 'test_site.vcf')

        self.assertTrue(vcf.read())
        self.assertFalse(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 0)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['A', 'A'], ['A', 'A'], ['A', 'A']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet, egglib.alphabets.DNA)
        self.assertEqual(site.as_list(), ['?', '?', 'A', 'A', 'A', 'A', 'A', 'A'])

        self.assertTrue(vcf.read())
        self.assertTrue(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 0)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['A', 'A'], ['A', 'A'], ['A', 'A']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet, egglib.alphabets.DNA)
        self.assertEqual(site.as_list(), ['?', '?', 'A', 'A', 'A', 'A', 'A', 'A'])

        self.assertTrue(vcf.read())
        self.assertFalse(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 1)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['ATG', 'ATG'], ['ATG', 'ATG'], ['ATG', 'ATG']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet.type, 'string')
        self.assertEqual(site.alphabet.get_alleles(), (['ATG'], ['?']))
        self.assertEqual(site.as_list(), ['?', '?', 'ATG', 'ATG', 'ATG', 'ATG', 'ATG', 'ATG'])

        self.assertTrue(vcf.read())
        self.assertTrue(vcf.is_snp()) # might depend on htslib
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 1)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['AAA', 'AAA'], ['AAA', 'AAA'], ['AAA', 'AAA']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet.type, 'string')
        self.assertEqual(site.alphabet.get_alleles(), (['AAA', 'AAC'], ['?']))
        self.assertEqual(site.as_list(), ['?', '?', 'AAA', 'AAA', 'AAA', 'AAA', 'AAA', 'AAA'])

        self.assertTrue(vcf.read())
        self.assertFalse(vcf.is_snp())
        self.assertFalse(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 1)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['ACG', 'ACG'], ['ACG', 'ACG'], ['ACG', 'ACG']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet.type, 'string')
        self.assertEqual(site.alphabet.get_alleles(), (['ACG', 'TAC'], ['?']))
        self.assertEqual(site.as_list(), ['?', '?', 'ACG', 'ACG', 'ACG', 'ACG', 'ACG', 'ACG'])

        self.assertTrue(vcf.read())
        self.assertTrue(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 0)
        self.assertEqual(vcf.get_genotypes(),
            [[None, None], ['A', 'A'], ['A', 'A'], ['A', 'G']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet, egglib.alphabets.DNA)
        self.assertEqual(site.as_list(), ['?', '?', 'A', 'A', 'A', 'A', 'A', 'G'])

        self.assertTrue(vcf.read())
        self.assertTrue(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 0)
        self.assertEqual(vcf.get_genotypes(),
            [['C', 'C'], [None, None], ['T', None], ['C', 'C']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet, egglib.alphabets.DNA)
        self.assertEqual(site.as_list(), ['C', 'C', '?', '?', 'T', '?', 'C', 'C'])

        self.assertTrue(vcf.read())
        self.assertTrue(vcf.is_snp())
        self.assertTrue(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 0)
        self.assertEqual(vcf.get_genotypes(),
            [['N', 'N'], ['-', '-'], [None, None], ['N', 'N']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet, egglib.alphabets.DNA)
        self.assertEqual(site.as_list(), ['N', 'N', '-', '-', '?', '?', 'N', 'N'])

        self.assertTrue(vcf.read())
        self.assertFalse(vcf.is_snp())
        self.assertFalse(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 1)
        self.assertEqual(vcf.get_genotypes(),
            [['A', 'A'], ['AA', None], ['AA', 'A'], ['A', 'AA']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet.type, 'string')
        self.assertEqual(site.alphabet.get_alleles(), (['A', 'AA', 'C'], ['?']))
        self.assertEqual(site.as_list(), ['A', 'A', 'AA', '?', 'AA', 'A', 'A', 'AA'])

        self.assertTrue(vcf.read())
        self.assertFalse(vcf.is_snp())
        self.assertFalse(vcf.is_single())
        self.assertEqual(vcf.get_allele_type(), 2)
        self.assertEqual(vcf.get_genotypes(),
            [['<all1>', '<all1>'], ['<all1>', '<all1>'], [None, None], ['<all2>', '<all2>']])
        site = vcf.as_site()
        self.assertEqual(site.alphabet.type, 'custom')
        self.assertEqual(site.alphabet.get_alleles(), (['<all1>', '<all2>'], ['?']))
        self.assertEqual(site.as_list(), ['<all1>', '<all1>', '<all1>', '<all1>', '?', '?', '<all2>', '<all2>'])

        for A1, A2 in [ ('G', 'G]17:198982]'),
                        ('T', ']13:123456]T'),
                        ('T', '<INV>'),
                        ('T', 'C<ctg1>'),
                        ('C', 'C[2 : 321682['),
                        ('A', ']2 : 321681]A'),
                        ('A', '<DUP>')]:
            self.assertTrue(vcf.read())
            self.assertFalse(vcf.is_snp())
            self.assertFalse(vcf.is_single())
            self.assertEqual(vcf.get_allele_type(), 2)
            self.assertEqual(vcf.get_genotypes(),
                [[A1, A1], [A1, A1], [A2, A2], [A2, A2]])
            site = vcf.as_site()
            self.assertEqual(site.alphabet.type, 'custom')
            self.assertEqual(site.alphabet.get_alleles(), ([A1, A2], ['?']))
            self.assertEqual(site.as_list(), [A1, A1, A1, A1, A2, A2, A2, A2])

        self.assertFalse(vcf.read())

    def test_iter_sites(self):

        # test dataset
        vcf_string = ("##fileformat=VCFv4.2\n"
        "##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n"
        "##contig=<ID=ctg1,length=1000>\n"
        "##contig=<ID=ctg2,length=1000>\n"
        "##contig=<ID=ctg3,length=1000>\n"
        "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n"
        "ctg1	1	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg1	2	.	C	G	.	PASS	.	GT	1|1	0|1	1|0	1|1\n"
        "ctg1	3	.	G	C	.	PASS	.	GT	0|1	1|1	0|0	0|0\n"
        "ctg1	5	.	T	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg1	6	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg1	7	.	G	T	.	PASS	.	GT	0|0	0|1	0|0	.|.\n"
        "ctg1	8	.	C	G	.	PASS	.	GT	0|0	0|0	0|0	0|0\n"
        "ctg1	9	.	G	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg1	10	.	T	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg1	11	.	A	C	.	PASS	.	GT	0|0	0|1	0|1	1|1\n"
        "ctg1	13	.	A	.	.	PASS	.	GT	0|0	0|0	0|0	0|0\n"
        "ctg2	4	.	C	T,*	.	PASS	.	GT	1|1	0|1	1|0	1|1\n"
        "ctg2	5	.	G	.	.	PASS	.	GT	0|0	0|0	0|0	.|.\n"
        "ctg2	6	.	G	C,T	.	PASS	.	GT	0|1	1|1	0|1	0|0\n"
        "ctg2	8	.	T	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg2	9	.	T	A	.	PASS	.	GT	0|0	0|1	.|.	1|1\n"
        "ctg2	10	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg2	11	.	G	GGGTC	.	PASS	.	GT	0|0	0|1	.|.	1|1\n"
        "ctg2	12	.	C	A	.	PASS	.	GT	1|1	0|1	0|0	1|1\n"
        "ctg2	14	.	G	C	.	PASS	.	GT	1|1	1|1	1|1	1|1\n"
        "ctg2	15	.	G	C	.	PASS	.	GT	0|0	0|0	.|.	1|1\n"
        "ctg2	16	.	T	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n"
        "ctg2	17	.	T	AAAAC	.	PASS	.	GT	1|1	1|1	1|1	1|1\n")

        # class to create iterable expectation based on the VCF string
        class Expectation:
            Item = collections.namedtuple('ExpectationItem', ['ctg', 'pos', 'GT'])

            def __init__(self, parent, vcf_string, chrom=None, start=None, stop=None, max_missing=0, mode=0):
                self.parent = parent
                lines = vcf_string.rstrip('\n').split('\n')
                self.items = []
                self.num = 0

                for line in lines:
                    if line[0] == '#': continue
                    bits = line.split('\t')
                    ctg = bits[0]
                    if chrom is not None and ctg != chrom: continue
                    pos = int(bits[1])-1
                    if start is not None and pos < start: continue
                    if stop is not None and pos >= stop: return
                    alls = {'.': '?', '0': bits[3]}
                    if bits[4] != '.':
                        for i, a in enumerate(bits[4].split(',')):
                            alls[str(i+1)] = a
                    if mode==0 and (not set(alls.values()) <= {'A', 'C', 'G', 'T', '*', '?'} or len(alls) == 2):  continue
                    if mode==1 and not set(alls.values()) <= {'A', 'C', 'G', 'T', '*', '?'}:  continue
                    parent.assertEqual(bits[8], 'GT')
                    GT = []
                    for bit in bits[9:]:
                        a, b = re.split('[|/]', bit)
                        GT.append(alls[a])
                        GT.append(alls[b])
                    if GT.count('?') > max_missing: continue
                    self.items.append(self.Item(ctg, pos, GT))
                    self.num += 1

            def __iter__(self):
                return iter(self.items)

        # create temporary files
        handler = TempfileHelper(vcf_string)

        # default VCF (no index
        vcf = egglib.io.VCF(handler.bcf)

        # the comparison function (I AM COMPACTOR)
        def cmp_f(num, **args):
            n = 0
            for site, expect in zip(vcf.iter_sites(**args),
                                    Expectation(self, vcf_string, **args),
                                    strict=True):
                self.assertEqual(expect.ctg, site.chrom)
                self.assertEqual(expect.pos, site.position)
                self.assertEqual(expect.GT, site.as_list())
                n += 1
            self.assertEqual(n, num)

        # test default setting
        cmp_f(num=16)

        # not possible to set chromosome without index
        with self.assertRaises(ValueError):
            vcf.iter_sites(chrom='ctg1')

        # VCF with index
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)

        # process full chromosomes
        cmp_f(chrom='ctg2', num=7)
        cmp_f(chrom='ctg1', num=9)

        # not possible to use start without chromosome
        with self.assertRaises(ValueError):
            vcf.iter_sites(start=0)

        # not possible to use negative start
        with self.assertRaises(ValueError):
            vcf.iter_sites(chrom='ctg1', start=-1)

        # start=0 gives the same result
        cmp_f(chrom='ctg1', start=0, num=9)

        # skip 3 sites
        cmp_f(chrom='ctg1', start=4, num=6)

        # pick just one site
        cmp_f(chrom='ctg1', start=10, num=1)

        # skip all sites
        cmp_f(chrom='ctg1', start=11, num=0)
        cmp_f(chrom='ctg1', start=140, num=0)

        # not possible to use stop without chromosome
        with self.assertRaises(ValueError):
            vcf.iter_sites(stop=0)

        # not possible to use negative stop
        with self.assertRaises(ValueError):
            vcf.iter_sites(chrom='ctg1', stop=-1)

        # last stop gives the same result
        cmp_f(chrom='ctg1', stop=100, num=9)
        cmp_f(chrom='ctg1', stop=11, num=9)

        # skipping some sites
        cmp_f(chrom='ctg1', stop=10, num=8)
        cmp_f(chrom='ctg1', stop=9, num=7)
        cmp_f(chrom='ctg2', stop=100, num=7)
        cmp_f(chrom='ctg2', stop=16, num=7)
        cmp_f(chrom='ctg2', stop=15, num=6)
        cmp_f(chrom='ctg2', stop=14, num=6)

        # skip all sites
        cmp_f(chrom='ctg1', stop=0, num=0)
        cmp_f(chrom='ctg1', stop=1, num=1)
        cmp_f(chrom='ctg2', stop=0, num=0)
        cmp_f(chrom='ctg2', stop=1, num=0)
        cmp_f(chrom='ctg2', stop=3, num=0)
        cmp_f(chrom='ctg2', stop=4, num=1)

        # start and stop
        cmp_f(chrom='ctg1', start=5, stop=9, num=3)
        cmp_f(chrom='ctg2', start=4, stop=13, num=4)

        # not possible to use negative max_missing
        with self.assertRaises(ValueError):
            vcf.iter_sites(max_missing=-1)

        # default max_missing value
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx) # VCF file must be reset
        cmp_f(max_missing=0, num=16)

        # increase parameters but without any additional sites
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=1, num=16)

        # consider more sites
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=2, num=19)

        # invalid mode values
        with self.assertRaises(ValueError):
            vcf.iter_sites(mode=3)
        with self.assertRaises(ValueError):
            vcf.iter_sites(mode=-1)
        with self.assertRaises(ValueError):
            vcf.iter_sites(mode='0')
        with self.assertRaises(ValueError):
            vcf.iter_sites(mode=None)

        # mode (confirm default value)
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=0, num=16,  mode=0)
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=2, num=19,  mode=0)

        # allow invariants
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=0, num=17,  mode=1)
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=2, num=21,  mode=1)

        # allow all
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=0, num=18,  mode=2)
        vcf = egglib.io.VCF(handler.bcf, index=handler.idx)
        cmp_f(max_missing=2, num=23,  mode=2)

##### add methods to test accessors ####################################

accessor_data = {
    'chrom': ['ctg1', 'ctg1', 'ctg1', 'ctg1', 'ctg2', 'ctg2', 'ctg2', 'ctg2', 'ctg2', 'ctg3', 'ctg3'],
    'pos': [999, 1000, 1009, 1010, 1014, 1015, 1019, 1029, 1049, 1059, 1099],
    'id': [['snp1', 'first', 'zero'], ['snp11'], ['snp2'], ['snp21'], [],
           ['snp201', 'snp+'], ['snp3', 'snp3'], ['snp4'], ['snp5'], ['no_snp'], []],
    'reference': ['A', 'A', 'C', 'C', 'G', 'G', 'G', 'C', 'CTC', 'A', 'A'],
    'alternate': [['T'], ['AA'], ['G', 'T'], ['G', 'CTT'], ['TAA'],
                  ['GAA'], ['T'], ['A'], ['ATG'], ['C'], []],
    'alleles': [['A', 'T'], ['A', 'AA'], ['C', 'G', 'T'],
                ['C', 'G', 'CTT'], ['G', 'TAA'], ['G', 'GAA'],
                ['G', 'T'], ['C', 'A'], ['CTC', 'ATG'], ['A', 'C'], ['A']],
    'quality': [4, None, None, None, None, None, None, None, None, None, None],
    'filter': [[], [], ['triple'], ['triple', 'multi'], [], [], [], [], [], [], []],
    'errors': [[], [], [], [], [], [], [], [], [], [], []],
    'phased': [(True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [True], [True]]),
               (True, [[True], [True], [], [True]]),
               (False, [[True, True], [True, False], [False, False], [False, False]]),
               (False, [[True], [True], [False], [True]])],
    'types': [['SNP'], ['INDEL'], ['SNP'], ['SNP', 'INDEL'], ['OTHER'],
              ['INDEL'], ['SNP'], ['SNP'], ['MNP'], ['SNP'], []],
    'is_snp': [True, False, True, False, False, False, True, True, False, True, False],
    'is_single': [True, False, True, False, False, False, True, True, False, True, True],
    'allele_type': [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0],
    'genotypes': [
        [ ['A', 'A'], ['A', 'T'], ['A', 'A'], ['T', 'T'] ],
        [ ['A', 'A'], ['A', 'AA'], ['A', 'A'], ['AA', 'AA'] ],
        [ ['G', 'G'], ['C', 'G'], ['G', 'C'], ['T', 'T'] ],
        [ ['G', 'G'], ['C', 'G'], ['G', 'C'], ['CTT', 'CTT'] ],
        [ ['G', 'TAA'], ['TAA', 'TAA'], ['G', 'G'], ['G', 'G'] ],
        [ ['G', 'GAA'], ['GAA', 'GAA'], ['G', 'G'], ['G', 'G'] ],
        [ ['G', 'G'], ['G', 'T'], ['G', 'G'], ['T', 'T'] ],
        [ ['C', 'C'], ['C', 'A'], ['C', 'C'], ['A', 'A'] ],
        [ ['CTC', 'CTC'], ['CTC', 'ATG'], [None], ['ATG', 'ATG'] ],
        [ ['A', 'A', 'A'], ['A', 'A', 'A'], ['A', 'A', 'C'], ['A', 'C', 'C'] ],
        [ ['A', 'A'], ['A', None], [None, None], [None, None] ]
    ]}

for what in accessor_data:
    def f(self, what=what):
        attr = what if what in ['is_snp', 'is_single'] else f'get_{what}'
        for ext in 'vcf', 'bcf':
            vcf = egglib.io.VCF(fname=path / f'b.{ext}')
            for i, v in enumerate(accessor_data[what]):
                self.assertTrue(vcf.read(), msg=f'read() returned False extension={ext} variant=#{i+1} what={what}')
                val = getattr(vcf, attr)()
                self.assertEqual(val, v,
                    msg=f'extension={ext} variant=#{i+1} what={what} exp={v} received={val}')
            self.assertFalse(vcf.read(), msg=f'extra read() returned True extension={ext} what={what}')
    setattr(VCF_test, f'test_{what}', f)

##### VCF slider #######################################################

class VcfSlider_test(unittest.TestCase):
    vcf1 = ('##fileformat=VCFv4.1\n'
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
            '##contig=<ID=ctg1,length=1000000>\n'
            '##contig=<ID=ctg2,length=1000000>\n'
            '##contig=<ID=ctg3,length=1000000>\n'
            '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n'
            'ctg1	1	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	2	.	A	C	.	PASS	.	GT	1|1	0|1	1|0	1|1\n'
            'ctg1	3	.	A	C	.	PASS	.	GT	0|1	1|1	0|0	0|0\n'
            'ctg1	5	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	6	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	8	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	9	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	10	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	1	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	2	.	A	C	.	PASS	.	GT	1|1	0|1	1|0	1|1\n'
            'ctg2	3	.	A	C	.	PASS	.	GT	0|1	1|1	0|0	0|0\n'
            'ctg2	4	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	5	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n')

    vcf2 = vcf1 + ('ctg3	7	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	7	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	8	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	10	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	15	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	15	.	A	C,AA	.	PASS	.	GT	0|0	1|1	0|0	0|0\n'
                   'ctg3	17	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	22	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	23	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	24	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	25	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	26	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	27	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	30	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	32	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	35	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	36	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	37	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	38	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	39	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	45	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	48	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	63	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	79	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	80	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	81	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	82	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	83	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	84	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	85	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	86	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	87	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	88	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	89	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	90	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	92	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	95	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	96	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	97	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	98	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	99	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	100	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	101	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	102	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	103	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	105	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	107	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	108	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
                   'ctg3	109	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n')

    vcf3 = ('##fileformat=VCFv4.2\n'
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
            '##contig=<ID=ctg1,length=1000000>\n'
            '##contig=<ID=ctg2,length=1000000>\n'
            '##contig=<ID=ctg3,length=1000000>\n'
            '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n'
            'ctg1	4	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	7	.	A	C	.	PASS	.	GT	1|1	0|1	1|0	1|1\n'
            'ctg1	10	.	A	C	.	PASS	.	GT	0|1	1|1	0|0	0|0\n'
            'ctg1	12	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg1	15	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	7	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	10	.	A	C	.	PASS	.	GT	1|1	0|1	1|0	1|1\n'
            'ctg2	12	.	A	C	.	PASS	.	GT	0|1	1|1	0|0	0|0\n'
            'ctg2	15	.	A	C	.	PASS	.	GT	0|0	0|1	0|0	1|1\n'
            'ctg2	24	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg2	26	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg2	28	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg2	29	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg2	30	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg3	1	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg3	2	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg3	3	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg3	4	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg3	5	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n')

    vcf4 = ('##fileformat=VCFv4.2\n'
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
            '##contig=<ID=ctg1,length=1000000>\n'
            '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n'
            'ctg1	4	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	8	.	A	C,G	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	10	.	A	C	.	PASS	.	GT	0|0	.|.	1|1	1|1\n'
            'ctg1	11	.	A	C,T	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	12	.	ACAC	A	.	PASS	.	GT	0|0	0|0	.|.	1|1\n'
            'ctg1	14	.	A	C,*	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	18	.	A	AC	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	22	.	A	C	.	PASS	.	GT	0|0	.|.	1|1	.|.\n'
            'ctg1	25	.	A	C,G	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	26	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	30	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	31	.	T	]13 : 123456]AGTNNNNNCAT	.	PASS	.	GT	0|0	0|0	0|0	1|1\n'
            'ctg1	39	.	AT	A	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	40	.	A	C,*	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	44	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	48	.	A	C	.	PASS	.	GT	0|0	.|.	.|.	1|1\n'
            'ctg1	55	.	A	C,G,T	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	56	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	58	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	62	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	65	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	66	.	A	C	.	PASS	.	GT	0|0	.|.	.|.	1|1\n'
            'ctg1	67	.	A	C	.	PASS	.	GT	0|0	.|.	1|1	1|1\n'
            'ctg1	70	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n')

    vcf5 = ('##fileformat=VCFv4.2\n'
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
            '##contig=<ID=ctg1,length=1000000>\n'
            '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	INDIV1	INDIV2	INDIV3	INDIV4\n'
            'ctg1	1	.	A	C	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	2	.	A	C,G	.	PASS	.	GT	0|0	0|0	1|1	2|2\n'
            'ctg1	4	.	A	C	.	PASS	.	GT	0|0	0|0	0|0	0|0\n'
            'ctg1	8	.	A	.	.	PASS	.	GT	0|0	0|0	0|0	0|0\n'
            'ctg1	16	.	A	C,ACC	.	PASS	.	GT	0|0	0|0	1|1	1|1\n'
            'ctg1	32	.	A	C	.	PASS	.	GT	1|1	1|1	1|1	1|1\n'
            'ctg1	64	.	A	.	.	PASS	.	GT	0|0	0|0	0|0	0|0\n')
 
    @staticmethod
    def window_check(s, wsize, wstep, as_variants, chrom=None):
        genome = collections.OrderedDict()
        for line in s.split('\n'):
            if len(line) == 0 or line[0] == '#': continue
            ch, p, *rest = line.split('\t')
            if ch not in genome: genome[ch] = []
            genome[ch].append(int(p)-1)
        res = {'ctg': [], 'bounds': [], 'len': [], 'span': [], 'sites': []}
        if chrom is None: keys = genome.keys()
        else: keys = [chrom]
        for ch in keys:
            c = 0
            while True:
                if as_variants:
                    win = genome[ch][c:c+wsize]
                    res['bounds'].append((win[0], win[-1]+1))
                else:
                    win = [i for i in genome[ch] if i>=c and i<c+wsize]
                    res['bounds'].append((c, c+wsize))
                res['ctg'].append(ch)
                res['len'].append(len(win))
                res['sites'].append(win)
                if len(win): res['span'].append(win[-1]-win[0]+1)
                else: res['span'].append(None)
                if as_variants:
                    if c+wsize >= len(genome[ch]): break
                    c += wstep
                    if c >= len(genome[ch]): break
                else:
                    if c+wsize > genome[ch][-1]: break
                    c += wstep
                    if c > genome[ch][-1]: break
        return res

    def setUp(self):
        self.handler1 = TempfileHelper(self.vcf1)
        self.handler2 = TempfileHelper(self.vcf2)
        self.handler3 = TempfileHelper(self.vcf3)
        self.handler4 = TempfileHelper(self.vcf4)
        self.handler5 = TempfileHelper(self.vcf5)

    def tearDown(self):
        self.handler1.close()
        self.handler2.close()
        self.handler3.close()
        self.handler4.close()
        self.handler5.close()

    def test_defaults(self):
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 4, 1)
        self.assertEqual(list(sld), [])
        self.assertEqual(len(sld), 0)
        with self.assertRaisesRegex(IndexError, '^site index out of range$'):
            self.assertEqual(sld[0])
        self.assertEqual(sld.span, None)
        self.assertEqual(sld.bounds, None)
        self.assertEqual(sld.chromosome, 'ctg1')

        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 4, 1, as_variants=True)
        self.assertEqual(list(sld), [])
        self.assertEqual(len(sld), 0)
        with self.assertRaisesRegex(IndexError, '^site index out of range$'):
            self.assertEqual(sld[0])
        self.assertEqual(sld.span, None)
        self.assertEqual(sld.bounds, None)
        self.assertEqual(sld.chromosome, 'ctg1')

    def test_chromosome(self):
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 4, 1)
        for i in range(7):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, 'ctg1')
        for i in range(2):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, 'ctg2')
        self.assertFalse(sld.move())

        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 4, 1, as_variants=True)
        for i in range(5):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, 'ctg1')
        for i in range(2):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, 'ctg2')
        self.assertFalse(sld.move())

    def test_size(self):
        # error
        vcf = egglib.io.VCF(self.handler1.bcf)
        with self.assertRaises(ValueError):
            sld = egglib.io.VcfSlider(vcf, 0, 1)

        # size=1
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 1, 1)
        ctrl = self.window_check(self.vcf1, 1, 1, as_variants=False)
        for i in range(len(ctrl['ctg'])):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, ctrl['ctg'][i])
            self.assertEqual(sld.bounds, ctrl['bounds'][i])
            self.assertEqual(sld.span, ctrl['span'][i])
            self.assertEqual(len(sld), ctrl['len'][i])
        self.assertFalse(sld.move())

        # as variants
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 1, 1, as_variants=True)
        ctrl = self.window_check(self.vcf1, 1, 1, as_variants=True)
        for i in range(len(ctrl['ctg'])):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, ctrl['ctg'][i])
            self.assertEqual(sld.bounds, ctrl['bounds'][i])
            self.assertEqual(sld.span, ctrl['span'][i])
            self.assertEqual(len(sld), ctrl['len'][i])
        self.assertFalse(sld.move())

        # size=3
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 3, 1)
        ctrl = self.window_check(self.vcf1, 3, 1, as_variants=False)
        for i in range(len(ctrl['ctg'])):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, ctrl['ctg'][i])
            self.assertEqual(sld.bounds, ctrl['bounds'][i])
            self.assertEqual(sld.span, ctrl['span'][i])
            self.assertEqual(len(sld), ctrl['len'][i])
        self.assertFalse(sld.move())

        # as variants
        vcf = egglib.io.VCF(self.handler1.bcf)
        sld = egglib.io.VcfSlider(vcf, 3, 1, as_variants=True)
        ctrl = self.window_check(self.vcf1, 3, 1, as_variants=True)
        for i in range(len(ctrl['ctg'])):
            self.assertTrue(sld.move())
            self.assertEqual(sld.chromosome, ctrl['ctg'][i])
            self.assertEqual(sld.bounds, ctrl['bounds'][i])
            self.assertEqual(sld.span, ctrl['span'][i])
            self.assertEqual(len(sld), ctrl['len'][i])
        self.assertFalse(sld.move())

    def test_step(self):
        # error
        vcf = egglib.io.VCF(self.handler2.bcf)
        with self.assertRaises(ValueError):
            sld = egglib.io.VcfSlider(vcf, 1, 0)

        # different steps
        for size in 1,2,3,4,5,6,7,8,9,10:
            for step in 1, 2, 3, 4, 5, 6, 7, 8, 9, 10:
                for varQ in 0, 1:
                    vcf = egglib.io.VCF(self.handler2.bcf)
                    sld = egglib.io.VcfSlider(vcf, size, step, mode=2, as_variants=varQ)
                    ctrl = self.window_check(self.vcf2, size, step, as_variants=varQ)
                    for i in range(len(ctrl['ctg'])):
                        msg = f'step={step} window #{i} (sites {ctrl["ctg"][i]}:{ctrl["bounds"][i]})'
                        self.assertTrue(sld.move(), msg=msg)
                        self.assertEqual(sld.chromosome, ctrl['ctg'][i], msg=msg)
                        self.assertEqual(sld.bounds, ctrl['bounds'][i], msg=msg)
                        self.assertEqual(sld.span, ctrl['span'][i], msg=msg)
                        self.assertEqual(len(sld), ctrl['len'][i], msg=msg)
                    self.assertFalse(sld.move())
    
    def test_chrom(self):
        vcf = egglib.io.VCF(self.handler2.bcf)
        with self.assertRaisesRegex(ValueError, '^an index is required$'):
            sld = egglib.io.VcfSlider(vcf, 5, 2, chrom='ctg1')

        for size in 1, 5, 10:
            for step in 1, 2, 5, 8, 10:
                for as_variants in False, True:
                    for ctg in 'ctg1', 'ctg2', 'ctg2':
                        vcf = egglib.io.VCF(self.handler2.bcf, self.handler2.idx)
                        sld = egglib.io.VcfSlider(vcf, size, step, chrom=ctg, as_variants=as_variants)
                        ctrl = self.window_check(self.vcf2, size, step, as_variants=as_variants, chrom=ctg)
                        for i in range(len(ctrl['ctg'])):
                            msg = f'window #{i} (sites {ctrl["ctg"][i]}:{ctrl["bounds"][i]})'
                            self.assertTrue(sld.move(), msg=msg)
                            self.assertEqual(sld.chromosome, ctrl['ctg'][i], msg=msg)
                            self.assertEqual(sld.bounds, ctrl['bounds'][i], msg=msg)
                            self.assertEqual(sld.span, ctrl['span'][i], msg=msg)
                            self.assertEqual(len(sld), ctrl['len'][i], msg=msg)
                        self.assertFalse(sld.move())

    def test_start(self):
        vcf = egglib.io.VCF(self.handler3.bcf, self.handler3.idx)
        with self.assertRaisesRegex(ValueError, '^cannot specify start or stop position without specifying chromosome$'):
            sld = egglib.io.VcfSlider(vcf, 5, 5, start=0)
        with self.assertRaisesRegex(ValueError, '^cannot specify start or stop position without specifying chromosome$'):
            sld = egglib.io.VcfSlider(vcf, 5, 5, stop=10)
        with self.assertRaises(ValueError):
            sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=-1)

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2')
        bnd = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
        num = [    0,       2,        2,        0,        1,        4]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=0)
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=5)
        bnd = [(5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
        num = [     2,        2,        0,        1,        4]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=6)
        bnd = [(6, 11), (11, 16), (16, 21), (21, 26), (26, 31)]
        num = [     2,        2,        0,        2,        3]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=7)
        bnd = [(7, 12), (12, 17), (17, 22), (22, 27), (27, 32)]
        num = [     2,        1,        0,        2,        3]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=8)
        bnd = [(8, 13), (13, 18), (18, 23), (23, 28), (28, 33)]
        num = [     2,        1,        0,        3,        2]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=10)
        bnd = [(10, 15), (15, 20), (20, 25), (25, 30)]
        num = [      2,        0,        1,        4]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=40)
        self.assertEqual(list(sld), [])

        # as variants

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=9, as_variants=True)
        num = [3, 3, 3, 2]
        bnd = [(9,15), (14, 26), (25, 29), (28, 30)]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=10, as_variants=True)
        num = [3, 3, 3]
        bnd = [(11,24), (23, 28), (27, 30)]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=14, as_variants=True)
        num = [3, 3, 2]
        bnd = [(14,26), (25, 29), (28, 30)]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

    def test_stop(self):
        vcf = egglib.io.VCF(self.handler3.bcf, self.handler3.idx)
        with self.assertRaisesRegex(ValueError, '^cannot specify start or stop position without specifying chromosome$'):
            sld = egglib.io.VcfSlider(vcf, 5, 5, stop=50)
        with self.assertRaises(ValueError):
            sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=-1)

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2')
        bnd = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
        num = [    0,       2,        2,        0,        1,        4]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=50)
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=29)
        bnd = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
        num = [    0,       2,        2,        0,        1,        3]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=25)
        bnd = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25)]
        num = [    0,       2,        2,        0,        1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=12)
        bnd = [(0, 5), (5, 10), (10, 15)]
        num = [    0,       2,        1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=10, stop=28)
        bnd = [(10, 15), (15, 20), (20, 25), (25, 30)]
        num = [      2,        0,        1,        2]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=15, stop=16)
        bnd = [(15, 20)]
        num = [      0]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=15, stop=15)
        bnd = []
        num = []
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', start=15, stop=14)
        bnd = []
        num = []
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 5, 5, chrom='ctg2', stop=2)
        bnd = [(0, 5)]
        num = [    0]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        # as variants

        sld = egglib.io.VcfSlider(vcf, 1, 2, chrom='ctg2', stop=70, as_variants=True)
        bnd = [(6,7), (11,12), (23, 24), (27, 28), (29, 30)]
        num = [1, 1, 1, 1, 1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 1, 2, chrom='ctg2', start=8, stop=70, as_variants=True)
        bnd = [(9,10), (14,15), (25, 26), (28, 29)]
        num = [1, 1, 1, 1, 1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 1, 2, chrom='ctg2', stop=27, as_variants=True)
        bnd = [(6,7), (11,12), (23, 24)]
        num = [1, 1, 1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 2, 2, chrom='ctg2', stop=28, as_variants=True)
        bnd = [(6,10), (11,15), (23, 26), (27, 28)]
        num = [    2,      2,        2,         1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=11, stop=24, as_variants=True)
        bnd = [(11,24)]
        num = [    3]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=11, stop=25, as_variants=True)
        bnd = [(11,24)]
        num = [    3]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=11, stop=22, as_variants=True)
        bnd = [(11,15)]
        num = [    2]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=11, stop=11, as_variants=True)
        bnd = []
        num = []
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=11, stop=12, as_variants=True)
        bnd = [(11, 12)]
        num = [1]
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

        sld = egglib.io.VcfSlider(vcf, 3, 2, chrom='ctg2', start=13, stop=14, as_variants=True)
        bnd = []
        num = []
        for i in range(len(bnd)):
            self.assertTrue(sld.move())
            self.assertEqual(sld.bounds, bnd[i])
            self.assertEqual(len(sld), num[i])
        self.assertFalse(sld.move())

    def test_max_missing_mode(self):
        vcf = egglib.io.VCF(self.handler4.bcf, self.handler4.idx)

        def cmp(size, step, as_variants, mode, max_missing, expect):
            sld = egglib.io.VcfSlider(vcf, size, step, chrom='ctg1', mode=mode, max_missing=max_missing, as_variants=as_variants)
            while sld.move():
                ref = expect.pop(0)
                self.assertEqual(sld.bounds, ref['bounds'])
                self.assertEqual(len(sld), ref['len'], msg=f'window={sld.bounds}')
                self.assertEqual(sld.span, ref['span'], msg=f'window={sld.bounds}')
            self.assertEqual(expect, [])

        for mm in 0, 1:
            cmp(size=10, step=10, as_variants=False, mode=0, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 2, 'span': 5},
                {'bounds': (10, 20), 'len': 2, 'span': 4},
                {'bounds': (20, 30), 'len': 3, 'span': 6},
                {'bounds': (30, 40), 'len': 1, 'span': 1},
                {'bounds': (40, 50), 'len': 1, 'span': 1},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 3, 'span': 9}])

            cmp(size=10, step=10, as_variants=False, mode=2, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 2, 'span': 5},
                {'bounds': (10, 20), 'len': 3, 'span': 8},
                {'bounds': (20, 30), 'len': 3, 'span': 6},
                {'bounds': (30, 40), 'len': 3, 'span': 10},
                {'bounds': (40, 50), 'len': 1, 'span': 1},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 3, 'span': 9}])

        for mm in 2, 3:
            cmp(size=10, step=10, as_variants=False, mode=0, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 3, 'span': 7},
                {'bounds': (10, 20), 'len': 2, 'span': 4},
                {'bounds': (20, 30), 'len': 3, 'span': 6},
                {'bounds': (30, 40), 'len': 1, 'span': 1},
                {'bounds': (40, 50), 'len': 1, 'span': 1},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 4, 'span': 9}])

            cmp(size=10, step=10, as_variants=False, mode=2, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 3, 'span': 7},
                {'bounds': (10, 20), 'len': 4, 'span': 8},
                {'bounds': (20, 30), 'len': 3, 'span': 6},
                {'bounds': (30, 40), 'len': 3, 'span': 10},
                {'bounds': (40, 50), 'len': 1, 'span': 1},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 4, 'span': 9}])

        for mm in 4, 5, 6, 7, 8:
            cmp(size=10, step=10, as_variants=False, mode=0, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 3, 'span': 7},
                {'bounds': (10, 20), 'len': 2, 'span': 4},
                {'bounds': (20, 30), 'len': 4, 'span': 9},
                {'bounds': (30, 40), 'len': 1, 'span': 1},
                {'bounds': (40, 50), 'len': 2, 'span': 5},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 5, 'span': 9}])

            cmp(size=10, step=10, as_variants=False, mode=2, max_missing=mm, expect=[
                {'bounds': (0, 10),  'len': 3, 'span': 7},
                {'bounds': (10, 20), 'len': 4, 'span': 8},
                {'bounds': (20, 30), 'len': 4, 'span': 9},
                {'bounds': (30, 40), 'len': 3, 'span': 10},
                {'bounds': (40, 50), 'len': 2, 'span': 5},
                {'bounds': (50, 60), 'len': 3, 'span': 4},
                {'bounds': (60, 70), 'len': 5, 'span': 9}])

        for mm in 0, 1:
            cmp(size=5, step=5, as_variants=True, mode=0, max_missing=mm, expect=[
                {'bounds': (3, 25),  'len': 5, 'span': 22},
                {'bounds': (25, 55), 'len': 5, 'span': 30},
                {'bounds': (55, 70), 'len': 5, 'span': 15}])

            cmp(size=5, step=5, as_variants=True, mode=2, max_missing=mm, expect=[
                {'bounds': (3, 18),  'len': 5, 'span': 15},
                {'bounds': (24, 39), 'len': 5, 'span': 15},
                {'bounds': (39, 58), 'len': 5, 'span': 19},
                {'bounds': (61, 70), 'len': 3, 'span': 9}])

        for mm in 2, 3:
            cmp(size=5, step=5, as_variants=True, mode=0, max_missing=mm, expect=[
                {'bounds': (3, 14),  'len': 5, 'span': 11},
                {'bounds': (24, 44), 'len': 5, 'span': 20},
                {'bounds': (54, 65), 'len': 5, 'span': 11},
                {'bounds': (66, 70), 'len': 2, 'span': 4}])

        for mm in 2, 3:
            cmp(size=5, step=5, as_variants=True, mode=2, max_missing=mm, expect=[
                {'bounds': (3, 12),  'len': 5, 'span': 9},
                {'bounds': (13, 30), 'len': 5, 'span': 17},
                {'bounds': (30, 55), 'len': 5, 'span': 25},
                {'bounds': (55, 67), 'len': 5, 'span': 12},
                {'bounds': (69, 70), 'len': 1, 'span': 1}])

        for mm in 4, 5, 6, 7, 8:
            cmp(size=5, step=5, as_variants=True, mode=0, max_missing=mm, expect=[
                {'bounds': (3, 14),  'len': 5, 'span': 11},
                {'bounds': (21, 40), 'len': 5, 'span': 19},
                {'bounds': (43, 58), 'len': 5, 'span': 15},
                {'bounds': (61, 70), 'len': 5, 'span': 9}])

        for mm in 4, 5, 6, 7, 8:
            cmp(size=5, step=5, as_variants=True, mode=2, max_missing=mm, expect=[
                {'bounds': (3, 12),  'len': 5, 'span': 9},
                {'bounds': (13, 26), 'len': 5, 'span': 13},
                {'bounds': (29, 44), 'len': 5, 'span': 15},
                {'bounds': (47, 62), 'len': 5, 'span': 15},
                {'bounds': (64, 70), 'len': 4, 'span': 6}])

        vcf = egglib.io.VCF(self.handler5.bcf, self.handler5.idx)

        cmp(size=3, step=1, as_variants=True, mode=0, max_missing=0, expect=[
            {'bounds': (0, 4),  'len': 3, 'span': 4},
            {'bounds': (1, 32),  'len': 3, 'span': 31}])

        cmp(size=3, step=1, as_variants=True, mode=1, max_missing=0, expect=[
            {'bounds': (0, 4),  'len': 3, 'span': 4},
            {'bounds': (1, 8),  'len': 3, 'span': 7},
            {'bounds': (3, 32),  'len': 3, 'span': 29},
            {'bounds': (7, 64),  'len': 3, 'span': 57}])

        cmp(size=3, step=1, as_variants=True, mode=2, max_missing=0, expect=[
            {'bounds': (0, 4),  'len': 3, 'span': 4},
            {'bounds': (1, 8),  'len': 3, 'span': 7},
            {'bounds': (3, 16),  'len': 3, 'span': 13},
            {'bounds': (7, 32),  'len': 3, 'span': 25},
            {'bounds': (15, 64),  'len': 3, 'span': 49}])
