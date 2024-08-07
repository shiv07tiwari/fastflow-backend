from nodes import combine_text, user_input, gemini, web_scraper, file_reader, resume_analysis, summarizer, zip_reader, \
    reddit_bot, company_enrichment, scoring, extractor, human_approval, filter
from nodes.constants import NodeModelTypes
from nodes.file_processing import sheet_writer


class Tables:
    WorkflowSchema = "workflow_schema"
    WorkFlowNode = "workflow_node"
    Node = "node"
    WorkflowRun = "workflow_run"


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
    NodeModelTypes.FilterNode: filter.FilterNode
}
