from glossator.corpus.snapshots import (
    DEFAULT_MANIFEST,
    REPOSITORY_ROOT,
    corpus_digest,
    read_snapshot_manifest,
    snapshot_corpus_dir,
)


def test_vendored_snapshot_directories_match_the_manifest() -> None:
    snapshots = read_snapshot_manifest(DEFAULT_MANIFEST)

    assert len(snapshots) == 8
    for snapshot in snapshots:
        corpus_dir = snapshot_corpus_dir(snapshot)
        assert corpus_dir.is_relative_to(REPOSITORY_ROOT)
        assert corpus_digest(corpus_dir) == snapshot.content_digest
