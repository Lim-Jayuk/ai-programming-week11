import pytest

from load_scores import load_scores


def write_csv(tmp_path, content):
    path = tmp_path / "scores_test.csv"
    path.write_text(content, encoding="utf-8-sig")
    return path


def test_정상적인_이름과_점수를_읽는다(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n민수,80\n지수,95\n")
    kept, skipped = load_scores(path)
    assert kept == [("민수", 80), ("지수", 95)]
    assert skipped == []


def test_헤더만_있으면_빈_목록을_반환한다(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n")
    assert load_scores(path) == ([], [])


def test_파일이_없으면_FileNotFoundError(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "없는파일.csv")


@pytest.mark.parametrize(
    "row, reason",
    [
        ("민수", "열 개수가 2가 아님"),
        ("민수,80,추가", "열 개수가 2가 아님"),
        (",80", "이름이 비어 있음"),
        ("민수,", "점수가 비어 있음"),
        ("민수,팔십", "점수가 정수가 아님"),
        ("민수,-1", "점수가 0~100 밖"),
        ("민수,101", "점수가 0~100 밖"),
    ],
)
def test_잘못된_행은_건너뛰고_이유를_기록한다(tmp_path, row, reason):
    path = write_csv(tmp_path, f"이름,점수\n{row}\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][1] == row
    assert skipped[0][2] == reason


def test_경계값_0과_100은_유효하다(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n영점,0\n백점,100\n")
    kept, skipped = load_scores(path)
    assert kept == [("영점", 0), ("백점", 100)]
    assert skipped == []


def test_동명이인은_둘다_남긴다(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n민수,70\n민수,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("민수", 70), ("민수", 90)]
    assert skipped == []


def test_빈줄은_기록없이_건너뛴다(tmp_path):
    path = write_csv(tmp_path, "이름,점수\n민수,80\n\n지수,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("민수", 80), ("지수", 90)]
    assert skipped == []
