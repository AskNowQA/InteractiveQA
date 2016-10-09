package tech.sda.iqa.sparql.jena;

import com.hp.hpl.jena.query.Query;
import com.hp.hpl.jena.query.QueryExecution;
import com.hp.hpl.jena.query.QueryExecutionFactory;
import com.hp.hpl.jena.query.QueryFactory;
import com.hp.hpl.jena.query.ResultSet;

public class QueryExecutor {
	public static ResultSet query(String sparql){
		Query query = QueryFactory.create(sparql);
		QueryExecution qExe = QueryExecutionFactory.sparqlService( "http://dbpedia.org/sparql", query );
		ResultSet results = qExe.execSelect();
		return results;
	}

}
