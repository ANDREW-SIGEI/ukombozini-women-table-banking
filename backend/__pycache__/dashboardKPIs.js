async function handler({ timeRange = 3 }) {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - parseInt(timeRange));
  
      const queries = [
        sql`
          SELECT 
            COUNT(DISTINCT m.id) as total_members,
            COUNT(CASE WHEN l.status = 'active' THEN l.id END) as active_loans,
            ROUND(AVG(l.amount)::numeric, 2) as avg_loan_amount,
            ROUND((COUNT(CASE WHEN l.status = 'defaulted' THEN l.id END)::float / NULLIF(COUNT(l.id), 0) * 100)::numeric, 2) as default_rate
          FROM members m
          LEFT JOIN loans l ON m.id = l.member_id
          WHERE m.created_at >= ${startDate} AND m.created_at <= ${endDate}
        `,
  
        sql`
          SELECT 
            COALESCE(SUM(amount), 0) as total_savings,
            COUNT(DISTINCT member_id) as saving_members,
            ROUND(AVG(amount)::numeric, 2) as avg_savings
          FROM savings_transactions
          WHERE created_at >= ${startDate} AND created_at <= ${endDate}
        `,
  
        sql`
          SELECT 
            COUNT(*) as total_groups,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_groups,
            ROUND(AVG(
              SELECT COUNT(*) 
              FROM members m 
              WHERE m.group_id = g.group_id
            )::numeric, 2) as avg_group_size
          FROM groups g
          WHERE created_at >= ${startDate} AND created_at <= ${endDate}
        `,
  
        sql`
          SELECT * FROM (
            SELECT 
              'member' as type,
              id as activity_id,
              'New member joined' as description,
              created_at
            FROM members 
            WHERE created_at >= ${startDate}
            UNION ALL
            SELECT 
              'loan' as type,
              id as activity_id,
              'Loan processed' as description,
              created_at
            FROM loans
            WHERE created_at >= ${startDate}
            UNION ALL
            SELECT 
              'group' as type,
              id as activity_id,
              'Group registered' as description,
              created_at
            FROM groups
            WHERE created_at >= ${startDate}
          ) activities
          ORDER BY created_at DESC
          LIMIT 10
        `,
      ];
  
      const [loanKPIs, savingsMetrics, groupMetrics, recentActivities] =
        await sql.transaction(queries);
  
      return {
        success: true,
        data: {
          loan_kpis: loanKPIs[0],
          savings_metrics: savingsMetrics[0],
          group_metrics: groupMetrics[0],
          recent_activities: recentActivities,
        },
      };
    } catch (error) {
      console.error("Error fetching dashboard KPIs:", error);
      return {
        success: false,
        error: "Failed to fetch dashboard statistics",
      };
    }
  }