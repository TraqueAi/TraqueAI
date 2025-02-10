from qdrant_client import QdrantClient, models
from bayesrag.embedder import get_embedding
from loguru import logger
from bayesrag.config import QDRANT_HOST,QDRANT_COLLECTION
class VectorDB:
    def __init__(self, collection_name=QDRANT_COLLECTION, qdrant_host=QDRANT_HOST):
        self.collection_name = collection_name
        self.qclient = QdrantClient(url=qdrant_host)

    def create_db(self):
        if self.qclient.collection_exists(collection_name=self.collection_name):
            logger.debug(f"Vector DB already exists: {self.collection_name}")
        else:
            self.qclient.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )
            logger.info(f"Vector DB successfully created: {self.collection_name}")

    def search_vector(self, query_embedding, limit=1):
        results = self.qclient.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
        )
        if results:
            top_result = results[0]
            return top_result.payload["data"], top_result.score
        else:
            logger.warning("No results found")
            return None, None

    def upsert_embeddings(self, chunks):
        logger.info("Upserting embeddings into Vector DB...")
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk.page_content)
            self.qclient.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=i, vector=embedding, payload={"data": chunk.page_content, "metadata": chunk.metadata}
                    ),
                ],
            )
        logger.info("Embeddings created successfully")

    def merge_embeddings(self, source_points):
        for point in source_points:
            self.qclient.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=point.payload
                    ),
                ],
            )
        logger.info("Merging embeddings successfully")
