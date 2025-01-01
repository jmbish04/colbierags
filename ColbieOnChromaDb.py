class ChromaDBManager:
    def __init__(
        self,
        cf_account_id: str,
        cf_api_token: str,
        cf_vectorize_index_name: str,
        collection_name: str = "default_collection",
        embedding_function: Optional[Any] = None,
        source_bucket_name: Optional[str] = None,
        source_prefix: Optional[str] = None,
        project_id: Optional[str] = None,
        extension_filter: Optional[str] = None,
        **kwargs: Any,
    ):
        self.cf_account_id = cf_account_id
        self.cf_api_token = cf_api_token
        self.cf_vectorize_index_name = cf_vectorize_index_name
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        self.source_bucket_name = source_bucket_name
        self.source_prefix = source_prefix
        self.project_id = project_id
        self.extension_filter = extension_filter
        self.vector_store = self._get_vector_store()
        # self.vector_store = self.client.get_or_create_collection(
        #     name=collection_name,
        #     embedding_function=embedding_function if embedding_function else None,
        # )

    def _get_vector_store(self) -> CloudflareVectorizeStore:
      """
      Gets a Cloudflare Vectorize store instance.

      """

      vector_store = CloudflareVectorizeStore(
          # embedding=self.embedding_function, # Vectorize currently defaults to text-embedding-ada-002
          index_name=self.cf_vectorize_index_name,
          account_id=self.cf_account_id,
          api_token=self.cf_api_token
      )

      return vector_store

    def _download_chroma_from_gcs(self) -> None:
        """Downloads a ChromaDB persist directory from GCS."""
        # No longer needed with CF
        pass

    def get_db_info(self) -> Dict:
        """Gets information about the Vectorize database."""

        index = self.vector_store.get_index()

        return {
            "index_name": self.index_name,
            "vector_count": index.describe()["vectors.ts"],  # Assuming this returns the vector count
            "dimensions": index.describe()["dimensions"],  # Assuming this returns the dimensions
        }

    def add_data(
        self,
        documents: Optional[Documents] = None,
        embeddings: Optional[Embeddings] = None,
        metadatas: Optional[Metadatas] = None,
        ids: Optional[IDs] = None # added to match method signature
    ) -> None:
        """
        Adds document chunks to the Vectorize index.

        Args:
            chunks (list): List of document chunks (text content) to add.
            embeddings (Optional[Embeddings]): List of embeddings corresponding to the chunks.
            metadatas (Optional[Metadatas]): List of metadata dictionaries corresponding to the chunks.
        """

        if documents and self.embedding_function:
          # Generate embeddings using the provided embedding function
          embeddings = self.embedding_function.embed_documents(documents)

        # Add data to the Vectorize store
        self.vector_store.add_texts(
            texts=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )


    def get_data(
        self,
        ids: Optional[IDs] = None,
        where: Optional[Where] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include: Include = ["embeddings", "documents", "metadatas"],
    ) -> GetResult:
        """
        Retrieves data from the ChromaDB collection.

        Args:
            ids (Optional[IDs]): List of document IDs to retrieve.
            where (Optional[Where]): Filter criteria for metadata.
            limit (Optional[int]): Maximum number of results to return.
            offset (Optional[int]): Offset for pagination.
            include (Include):  Data to include in the result.

        Returns:
            GetResult: The retrieved data.
        """
        return self.collection.get(
            ids=ids, where=where, limit=limit, offset=offset, include=include
        )

    def query(
        self,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[Embeddings] = None,
        n_results: int = 10,
        where: Optional[Where] = None,
        include: Include = ["embeddings", "documents", "metadatas", "distances"],
        **kwargs: Any,
    ) -> QueryResult:
        """Queries the ChromaDB collection.

        Args:
            query_texts: List of query texts.
            query_embeddings: List of query embeddings.
            n_results: Number of results to return.
            where: Filter criteria for metadata.
            include: Data to include in the result.

        Returns:
            QueryResult: The query results.
        """
        if query_embeddings is None and self.embedding_function and query_texts:
            query_embeddings = self.embedding_function.embed_query(query_texts)

        return self.vector_store.similarity_search_by_vector(
            embedding=query_embeddings,
            k=n_results,
            filter=where,  # Assuming 'where' can be used as a filter
            include=include
        )

    def update_data(
        self,
        ids: IDs,
        documents: Optional[Documents] = None,
        embeddings: Optional[Embeddings] = None,
        metadয়াস: Optional[Metadatas] = None,
    ) -> None:
        """Updates data in the ChromaDB collection.

        Args:
            ids: List of document IDs to update.
            documents: List of updated document texts.
            embeddings: List of updated document embeddings.
            metadatas: List of updated metadata dictionaries.
        """
        if embeddings is None and self.embedding_function and documents:
            embeddings = self.embedding_function.embed_documents(documents)

        self.vector_store.update_document(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def delete_data(
        self,
        ids: Optional[IDs] = None,
        where: Optional[Where] = None,
    ) -> None:
        """Deletes data from the ChromaDB collection.

        Args:
            ids: List of document IDs to delete.
            where: Filter criteria for metadata.
        """
        self.vector_store.delete(ids=ids, where=where)

    def save_to_gcs(self, prefix: Optional[str] = None) -> None:
        """Saves the ChromaDB to GCS."""
        # Not applicable for Cloudflare Vectorize
        pass

    def peek(self, n: int = 10) -> GetResult:
        """
        Returns a preview (peek) of the first n items in the database.

        Args:
            n (int): The number of items to preview.

        Returns:
            GetResult: A dictionary containing the first n items, similar to the output of the get() method.
        """
        # Assuming there's a way to get items from Cloudflare Vectorize, otherwise this will need adjustment.
        return self.vector_store.get(limit=n)

    def visualize(
        self,
        n_components: int = 3,
        method: str = "pca",
        perplexity: int = 30,
        n_iter: int = 1000,
        random_state: int = 42,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[Embeddings] = None,
        n_results: int = 10,
        where: Optional[Where] = None,
    ) -> None:
        """
        Visualizes document vectors.ts in 3D space using PCA or t-SNE.

        Args:
            n_components: The number of components for dimensionality reduction (should be 3 for 3D visualization).
            method: The dimensionality reduction method ('pca' or 'tsne').
            perplexity: The perplexity parameter for t-SNE.
            n_iter: The number of iterations for t-SNE.
            random_state: The random state for reproducibility.
            query_texts: Optional list of query texts for querying and visualizing specific results.
            query_embeddings: Optional list of query embeddings corresponding to query_texts.
            n_results: Number of results to return for the query if performed.
            where: Optional filter criteria for metadata when querying.
        """

        if query_texts or query_embeddings:
            # Perform a query to get specific results
            query_results = self.query(
                query_texts=query_texts,
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=["embeddings", "documents"],
            )
            if not query_results or not query_results["embeddings"]:
                print("No results found for the query.")
                return

            all_embeddings = query_results["embeddings"]
            all_contents = query_results["documents"]
        else:
            # Use get() to retrieve all data
            results = self.get_data(include=["embeddings", "documents"])

            if not results or not results["embeddings"]:
                print("No vectors.ts found in the database.")
                return

            all_embeddings = results["embeddings"]
            all_contents = results["documents"]

        # Convert embeddings to a NumPy array
        embedding_matrix = np.array(all_embeddings)

        # Dimensionality Reduction
        if method == "pca":
            reducer = PCA(n_components=n_components, random_state=random_state)
        elif method == "tsne":
            reducer = TSNE(
                n_components=n_components,
                perplexity=perplexity,
                n_iter=n_iter,
                random_state=random_state,
            )
        else:
            raise ValueError("Invalid dimensionality reduction method. Choose 'pca' or 'tsne'.")

        reduced_embeddings = reducer.fit_transform(embedding_matrix)

        # Create 3D Scatter Plot
        fig = go.Figure()

        fig.add_trace(
            go.Scatter3d(
                x=reduced_embeddings[:, 0],
                y=reduced_embeddings[:, 1],
                z=reduced_embeddings[:, 2],
                mode="markers",
                marker=dict(size=5, color="blue", opacity=0.8),
                text=all_contents,  # Use document contents as hover text
                hoverinfo="text",
            )
        )

        fig.update_layout(
            title="Document Vector Visualization",
            scene=dict(
                xaxis_title="Component 1",
                yaxis_title="Component 2",
                zaxis_title="Component 3",
            ),
        )

        fig.show()


manager = ChromaDBManager(
    cf_account_id=CF_ACCOUNT_ID,
    cf_api_token=CF_API_TOKEN,
    cf_vectorize_index_name=CF_VECTORIZE_INDEX_NAME,
    collection_name="colbie_v1",
    embedding_function=embedding_function,
    source_bucket_name=SOURCE_BUCKET_NAME,
    source_prefix=SOURCE_PREFIX,
    project_id=gcp_project_id,
    extension_filter=".md"
)