from langchain_community.vectorstores import FAISS
import os
from app.components.embeddings import get_embedding_model

from app.common.custom_exception import CustomException
from app.common.logger import get_logger
from app.config.config import DB_FAISS_PATH

logger = get_logger(__name__)

def load_vector_store():
    try:
        embedding_model = get_embedding_model()

        if os.path.exists(DB_FAISS_PATH):
            logger.info("Loading existing Vectorstore")

            return FAISS.load_local(
                DB_FAISS_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )
        
        else:
            logger.warning("No vectostore found")

    except Exception as e:
        error_message = CustomException("Failed to load vectostore",e)
        logger.error(str(error_message))


## For creating a new vectorstore
def save_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise CustomException("No text chunks to create vectorstore")
        
        logger.info("Creating new vectorstore")

        embedding_model = get_embedding_model()

        db = FAISS.from_documents(
            text_chunks,
            embedding_model
        )

        logger.info("Saving vectorstore...")


        db.save_local(DB_FAISS_PATH)

        logger.info("Vectorstore saved successfullly")

        return db
    except Exception as e:
        error_message = CustomException("Failed to save new Vectorstore",e)
        logger.error(str(error_message))