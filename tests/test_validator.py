import csv
import io
from pathlib import Path

from haystack_validator import validate_file, validate_rows
from haystack_validator.__main__ import main

HEADER = "id,dis,markers,equipRef,siteRef,kind,unit\n"
GOOD = HEADER + (
    "s,Site,site,,,,\n"
    "e,Equip,equip ahu,,s,,\n"
    "p,Point,point sensor air temp,e,,Number,degF\n"
)
EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "points.csv"


def rules(text: str) -> list[str]:
    return [i.rule for i in validate_rows(csv.DictReader(io.StringIO(text)))]


def test_clean_file_has_no_issues():
    assert rules(GOOD) == []


def test_missing_id():
    assert "H001" in rules(HEADER + ",x,site,,,,\n")


def test_duplicate_id_flagged_on_both_rows():
    assert rules(HEADER + "a,A,site,,,,\na,B,site,,,,\n").count("H002") == 2


def test_repeated_marker():
    assert "H003" in rules(HEADER + "a,A,site site,,,,\n")


def test_invalid_tag_name():
    assert "H004" in rules(HEADER + "a,A,site Bad-Tag,,,,\n")


def test_unknown_tag():
    assert "H005" in rules(HEADER + "a,A,site foobar,,,,\n")


def test_no_entity_tag():
    assert "H006" in rules(HEADER + "a,A,temp,,,,\n")


def test_two_entity_tags():
    assert "H006" in rules(HEADER + "a,A,site equip,,,,\n")


def test_point_without_function_tag():
    assert "H007" in rules(GOOD + "q,Q,point air temp,e,,Number,degF\n")


def test_point_with_two_function_tags():
    assert "H007" in rules(GOOD + "q,Q,point sensor sp temp,e,,Number,degF\n")


def test_dangling_equip_ref():
    assert "H008" in rules(GOOD + "q,Q,point sensor temp,nope,,Number,degF\n")


def test_equip_ref_must_be_an_equip():
    assert "H008" in rules(GOOD + "q,Q,point sensor temp,s,,Number,degF\n")


def test_equip_without_site_ref():
    assert "H008" in rules(HEADER + "e,E,equip ahu,,,,\n")


def test_bad_kind_and_missing_unit():
    found = rules(GOOD + "q,Q,point sensor temp,e,,Float,\nr,R,point sensor temp,e,,Number,\n")
    assert "H009" in found and "H010" in found


def test_line_numbers_start_after_header():
    issues = validate_rows(csv.DictReader(io.StringIO(HEADER + "a,A,site foobar,,,,\n")))
    assert issues[0].line == 2


def test_empty_rows_give_no_issues():
    assert validate_rows([]) == []


def test_cli_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.csv"
    good.write_text(GOOD, encoding="utf-8")
    assert main([str(good)]) == 0
    bad = tmp_path / "bad.csv"
    bad.write_text(HEADER + "a,A,foobar,,,,\n", encoding="utf-8")
    assert main([str(bad)]) == 1
    assert main([]) == 2
    assert main([str(tmp_path / "missing.csv")]) == 2
    assert "issue(s) found" in capsys.readouterr().out


def test_validate_file_reads_example():
    assert len(validate_file(EXAMPLE)) >= 8
