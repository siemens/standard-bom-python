# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
import unittest

from cyclonedx.model import ExternalReference, ExternalReferenceType, HashAlgorithm, HashType, XsUri
from cyclonedx.model.component import Component, ComponentType

from standardbom.model import SbomComponent, SOURCE_ARCHIVE_LOCAL, SourceArtifact, SOURCE_ARCHIVE_URL


class StandardBomSourcesTestCase(unittest.TestCase):
    def test_empty_sources(self):
        component = SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY))
        self.assertIsNotNone(component.sources)
        self.assertEqual(0, len(component.sources))

    def test_local_sources(self):
        component = SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY))

        self.assertIsNotNone(component.local_sources)
        self.assertEqual(0, len(component.local_sources))

        component.add_local_source(
            url="file:sources/226247b40160f2892fa4c7851b5b913d5d10912d/commons-codec-1.13-sources.jar",
            hashes=[])
        self.assertIsNotNone(component.sources)
        self.assertIsNotNone(component.local_sources)
        self.assertEqual(1, len(component.sources))
        self.assertEqual(1, len(component.local_sources))
        self.assertEqual("file:sources/226247b40160f2892fa4c7851b5b913d5d10912d/commons-codec-1.13-sources.jar",
                         component.sources[0].url)
        self.assertEqual("file:sources/226247b40160f2892fa4c7851b5b913d5d10912d/commons-codec-1.13-sources.jar",
                         component.local_sources[0].url)
        self.assertIsNone(component.local_sources[0].md5)
        self.assertIsNone(component.local_sources[0].sha1)
        self.assertIsNone(component.local_sources[0].sha256)
        self.assertIsNone(component.local_sources[0].sha512)

    def test_remote_sources(self):
        component = SbomComponent(Component(name="test.jar", type=ComponentType.LIBRARY))

        self.assertIsNotNone(component.remote_sources)
        self.assertEqual(0, len(component.remote_sources))

        component.add_remote_source(url="https://foo.bar/sources.jar", hashes=[])
        self.assertIsNotNone(component.sources)
        self.assertIsNotNone(component.remote_sources)
        self.assertEqual(1, len(component.sources))
        self.assertEqual(1, len(component.remote_sources))
        self.assertEqual("https://foo.bar/sources.jar", component.sources[0].url)
        self.assertEqual("https://foo.bar/sources.jar", component.remote_sources[0].url)
        self.assertIsNone(component.remote_sources[0].md5)
        self.assertIsNone(component.remote_sources[0].sha1)
        self.assertIsNone(component.remote_sources[0].sha256)
        self.assertIsNone(component.remote_sources[0].sha512)

    def test_remote_sources_constr(self):
        source_artifact = SourceArtifact(download_url='https://foo.bar/sources.jar')
        self.assertEqual("https://foo.bar/sources.jar", source_artifact.url)
        self.assertEqual(SOURCE_ARCHIVE_URL, source_artifact.external_ref.comment)
        self.assertEqual(ExternalReferenceType.DISTRIBUTION, source_artifact.type)
        self.assertEqual(0, len(source_artifact.external_ref.hashes))

    def test_local_sources_constr(self):
        source_artifact = SourceArtifact(local_file='file:///sources/abc123/sources.zip',
                                         hashes=[HashType(alg=HashAlgorithm.SHA_1, content='abc123')])
        self.assertEqual('file:///sources/abc123/sources.zip', source_artifact.url)
        self.assertEqual(SOURCE_ARCHIVE_LOCAL, source_artifact.external_ref.comment)
        self.assertEqual(ExternalReferenceType.DISTRIBUTION, source_artifact.type)
        self.assertEqual(1, len(source_artifact.external_ref.hashes))
        self.assertEqual('abc123', source_artifact.sha1)

    def test_sources_conflict(self):
        try:
            SourceArtifact(download_url='https://example.com/sources.jar', local_file='sources.jar')
        except ValueError as e:
            assert 'Cannot specify both local_file and download_url' in str(e)
        else:
            self.fail('ValueError was not raised')

    def test_sources_conflict2(self):
        try:
            SourceArtifact(external_ref=ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                                          comment='This will not work!',
                                                          url=XsUri("https://example.com/sources.jar")),
                           hashes=[HashType(alg=HashAlgorithm.MD5, content='abc')])
        except ValueError as e:
            self.assertEqual('external_ref must be the only argument', str(e))
        else:
            self.fail('ValueError was not raised')

    def test_source_artifact_md5(self):
        source_artifact = SourceArtifact(ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                                           comment=SOURCE_ARCHIVE_URL,
                                                           url=XsUri("https://foo.bar/sources.jar"),
                                                           hashes=[]))
        self.assertIsNone(source_artifact.md5)
        source_artifact.md5 = "test-md5"
        self.assertEqual("test-md5", source_artifact.md5)

    def test_source_artifact_sha1(self):
        source_artifact = SourceArtifact(ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                                           comment=SOURCE_ARCHIVE_URL,
                                                           url=XsUri("https://foo.bar/sources.jar"),
                                                           hashes=[]))
        self.assertIsNone(source_artifact.sha1)
        source_artifact.sha1 = "test-sha1"
        self.assertEqual("test-sha1", source_artifact.sha1)

    def test_source_artifact_sha256(self):
        source_artifact = SourceArtifact(ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                                           comment=SOURCE_ARCHIVE_URL,
                                                           url=XsUri("https://foo.bar/sources.jar"),
                                                           hashes=[]))
        self.assertIsNone(source_artifact.sha256)
        source_artifact.sha256 = "test-sha256"
        self.assertEqual("test-sha256", source_artifact.sha256)

    def test_source_artifact_sha512(self):
        source_artifact = SourceArtifact(ExternalReference(type=ExternalReferenceType.DISTRIBUTION,
                                                           comment=SOURCE_ARCHIVE_URL,
                                                           url=XsUri("https://foo.bar/sources.jar"),
                                                           hashes=[]))
        self.assertIsNone(source_artifact.sha512)
        source_artifact.sha512 = "test-sha512"
        self.assertEqual("test-sha512", source_artifact.sha512)

    def test_construct(self):
        source_artifact = SourceArtifact()
        self.assertEqual(ExternalReferenceType.DISTRIBUTION, source_artifact.type)
        self.assertEqual('https://example.com', source_artifact.url)

        source_artifact.type = ExternalReferenceType.WEBSITE
        source_artifact.url = 'https://example.com/second'
        self.assertEqual(ExternalReferenceType.WEBSITE, source_artifact.type)
        self.assertEqual('https://example.com/second', source_artifact.url)


if __name__ == '__main__':
    unittest.main()
