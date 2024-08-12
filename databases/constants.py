from nodes import combine_text, user_input, gemini, web_scraper, file_reader, resume_analysis, summarizer, zip_reader, \
    reddit_bot, company_enrichment, scoring, extractor, human_approval, filter, gemini_image, invoice_processor, yt_comments, gemini_rag
from nodes.constants import NodeModelTypes
from nodes.file_processing import sheet_writer
from nodes.google import google_sheet_writer, email_draft, google_sheet_reader
from nodes.star import data_analysis


class Tables:
    WorkflowSchema = "workflow_schema"
    WorkFlowNode = "workflow_node"
    Node = "node"
    WorkflowRun = "workflow_run"
    GoogleUser = "google_user"


class QueryOperations:
    LessThan = "<"
    LessThanEqualTo = "<="
    Equals = "=="
    GreaterThan = ">"
    GreaterThanEqualTo = ">="
    NotEquals = "!="
    ArrayContains = "array_contains"
    ArrayContainsAny = "array_contains_any"
    In = "in"
    NotIn = "not_in"


class QueryConstants:
    Node = "node"
    Workflow = "workflow"
    Id = "id"
    Owner = "owner"


NodeTypeClassMappings = {
    NodeModelTypes.CombineText: combine_text.CombineTextNode,
    NodeModelTypes.UserInput: user_input.UserInputNode,
    NodeModelTypes.WebScraper: web_scraper.WebScraperNode,
    NodeModelTypes.Gemini: gemini.GeminiNode,
    NodeModelTypes.FileReader: file_reader.FileReader,
    NodeModelTypes.ResumeAnalysis: resume_analysis.ResumeAnalysisNode,
    NodeModelTypes.SummarizerNode: summarizer.SummarizerNode,
    NodeModelTypes.ZipReaderNode: zip_reader.ZipReaderNode,
    NodeModelTypes.RedditBotNode: reddit_bot.RedditBotNode,
    NodeModelTypes.CompanyEnrichmentNode: company_enrichment.CompanyEnrichmentNode,
    NodeModelTypes.SheetWriterNode: sheet_writer.SheetWriterNode,
    NodeModelTypes.ScoringNode: scoring.ScoringNode,
    NodeModelTypes.ExtractorNode: extractor.ExtractorNode,
    NodeModelTypes.HumanApprovalNode: human_approval.HumanApproval,
    NodeModelTypes.FilterNode: filter.FilterNode,
    NodeModelTypes.GeminiImageNode: gemini_image.GeminiImageNode,
    NodeModelTypes.GoogleSheetWriterNode: google_sheet_writer.GoogleSheetWriterNode,
    NodeModelTypes.GoogleSheetReaderNode: google_sheet_reader.GoogleSheetReaderNode,
    NodeModelTypes.InvoiceProcessorNode: invoice_processor.InvoiceProcessorNode,
    NodeModelTypes.EmailDraftNode: email_draft.EmailDraftNode,
    NodeModelTypes.DataAnalysisNode: data_analysis.DataAnalysisNode,
    NodeModelTypes.GeminiRAG: gemini_rag.GeminiRAGNode,
    NodeModelTypes.YouTubeCommentsRetriever: yt_comments.YouTubeCommentsRetriever
}
