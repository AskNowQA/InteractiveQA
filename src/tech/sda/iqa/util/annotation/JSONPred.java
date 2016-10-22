package tech.sda.iqa.util.annotation;

import java.util.ArrayList;



//import org.json.simple.*;
import org.json.JSONArray;
import org.json.JSONObject;

public class JSONPred {
	static JSONArray create(ArrayList<String> wordlist, ArrayList<String> mAX1pcUri, ArrayList<Float> mAX1pcScore, 
			ArrayList<String> mAX2pcUri, ArrayList<Float> mAX2pcScore, ArrayList<String> mAX3pcUri, ArrayList<Float> mAX3pcScore){
		
//		array starts here
		JSONArray predicate = new JSONArray();
		
		for (int i = 0 ; i < wordlist.size(); i++ )
		{
			String word = wordlist.get(i);
			JSONObject jo_word_candidate = new JSONObject();
			JSONArray ja_candidates = new JSONArray();
			JSONObject jo_uri_score = new JSONObject();
			System.out.println(mAX1pcScore.get(i));
			System.out.println(mAX2pcScore.get(i));
			System.out.println(mAX3pcScore.get(i));
			jo_uri_score.put("uri", mAX1pcUri.get(i));
			jo_uri_score.put("score",mAX1pcScore.get(i));
			ja_candidates.put(jo_uri_score);

			jo_uri_score = new JSONObject();

			jo_uri_score.put("uri", mAX2pcUri.get(i));
			jo_uri_score.put("score",mAX2pcScore.get(i));
			ja_candidates.put(jo_uri_score);
			
			jo_uri_score = new JSONObject();
			
			jo_uri_score.put("uri", mAX3pcUri.get(i));
			jo_uri_score.put("score",mAX3pcScore.get(i));
			ja_candidates.put(jo_uri_score);
			
			jo_word_candidate.put("word", word);
			jo_word_candidate.put("candidates", ja_candidates);
			
			predicate.put(jo_word_candidate);
			
		}
		
		
		JSONObject predicate_json = new JSONObject();
		predicate_json.put("predicate", predicate);

		return predicate;
	};
}
