import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioDataProcessor:
    """Handles Excel file processing and portfolio data management"""
    
    def __init__(self):
        self.data = {}
        self.processed_data = {}
        
    def load_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Load and parse the multi-sheet Excel file"""
        try:
            # Read all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # Expected sheet names
            expected_sheets = [
                'Portfolio_Overview', 'Holdings_Detail', 'Historical_Performance',
                'Benchmarks', 'Risk_Metrics', 'Cash_Flows', 'Market_Data'
            ]
            
            # Validate sheets exist
            for sheet in expected_sheets:
                if sheet not in excel_data:
                    raise ValueError(f"Missing required sheet: {sheet}")
            
            self.data = excel_data
            logger.info(f"Successfully loaded {len(excel_data)} sheets")
            
            # Process and clean data
            self._clean_data()
            self._calculate_metrics()
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise
    
    def _clean_data(self):
        """Clean and standardize data across all sheets"""
        # Clean Portfolio Overview
        if 'Portfolio_Overview' in self.data:
            df = self.data['Portfolio_Overview']
            df['Inception_Date'] = pd.to_datetime(df['Inception_Date'])
            df['Last_Updated'] = pd.to_datetime(df['Last_Updated'])
            df['Total_AUM'] = pd.to_numeric(df['Total_AUM'], errors='coerce')
            df['Target_Return'] = pd.to_numeric(df['Target_Return'], errors='coerce')
        
        # Clean Holdings Detail
        if 'Holdings_Detail' in self.data:
            df = self.data['Holdings_Detail']
            df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'])
            numeric_cols = ['Market_Value', 'Units_Held', 'Average_Cost', 'Current_Price', 'Weight_Percent', 'Dividend_Yield']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean time series data
        time_series_sheets = ['Historical_Performance', 'Benchmarks', 'Risk_Metrics', 'Cash_Flows', 'Market_Data']
        for sheet_name in time_series_sheets:
            if sheet_name in self.data:
                df = self.data[sheet_name]
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                
                # Convert numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                self.data[sheet_name] = df
    
    def _calculate_metrics(self):
        """Calculate additional portfolio metrics"""
        self.processed_data = {}
        
        # Portfolio summary metrics
        if 'Portfolio_Overview' in self.data and 'Holdings_Detail' in self.data:
            portfolio = self.data['Portfolio_Overview'].iloc[0]
            holdings = self.data['Holdings_Detail']
            
            self.processed_data['portfolio_summary'] = {
                'fund_name': portfolio['Fund_Name'],
                'total_aum': portfolio['Total_AUM'],
                'base_currency': portfolio['Base_Currency'],
                'target_return': portfolio['Target_Return'],
                'risk_level': portfolio['Risk_Level'],
                'benchmark': portfolio['Benchmark'],
                'total_holdings': len(holdings),
                'total_market_value': holdings['Market_Value'].sum(),
                'inception_date': portfolio['Inception_Date']
            }
        
        # Top holdings
        if 'Holdings_Detail' in self.data:
            holdings = self.data['Holdings_Detail']
            top_holdings = holdings.nlargest(10, 'Market_Value')[
                ['Asset_Name', 'Ticker_Symbol', 'Market_Value', 'Weight_Percent', 'Sector']
            ].to_dict('records')
            self.processed_data['top_holdings'] = top_holdings
        
        # Sector allocation
        if 'Holdings_Detail' in self.data:
            holdings = self.data['Holdings_Detail']
            sector_allocation = holdings.groupby('Sector')['Market_Value'].sum().sort_values(ascending=False)
            self.processed_data['sector_allocation'] = sector_allocation.to_dict()
        
        # Performance metrics
        if 'Historical_Performance' in self.data:
            perf = self.data['Historical_Performance']
            latest_perf = perf.iloc[-1]
            
            self.processed_data['performance_summary'] = {
                'current_value': latest_perf['Portfolio_Value'],
                'total_return': latest_perf['Cumulative_Return'],
                'daily_return': latest_perf['Daily_Return'],
                'volatility': latest_perf['Volatility'],
                'sharpe_ratio': latest_perf['Sharpe_Ratio'],
                'max_drawdown': latest_perf['Max_Drawdown'],
                'active_return': latest_perf['Active_Return']
            }
        
        # Risk summary
        if 'Risk_Metrics' in self.data:
            risk = self.data['Risk_Metrics']
            latest_risk = risk.iloc[-1]
            
            self.processed_data['risk_summary'] = {
                'portfolio_beta': latest_risk['Portfolio_Beta'],
                'var_95': latest_risk['VaR_95'],
                'cvar_95': latest_risk['CVaR_95'],
                'tracking_error': latest_risk['Tracking_Error'],
                'correlation_benchmark': latest_risk['Correlation_Benchmark'],
                'concentration_risk': latest_risk['Concentration_Risk'],
                'liquidity_score': latest_risk['Liquidity_Score']
            }
    
    def get_time_series_data(self, sheet_name: str, columns: List[str] = None) -> pd.DataFrame:
        """Get time series data for charting"""
        if sheet_name not in self.data:
            raise ValueError(f"Sheet {sheet_name} not found")
        
        df = self.data[sheet_name].copy()
        if columns:
            columns_with_date = ['Date'] + [col for col in columns if col in df.columns]
            df = df[columns_with_date]
        
        return df
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get processed portfolio summary"""
        return self.processed_data.get('portfolio_summary', {})
    
    def get_holdings_data(self) -> Dict[str, Any]:
        """Get holdings analysis"""
        return {
            'top_holdings': self.processed_data.get('top_holdings', []),
            'sector_allocation': self.processed_data.get('sector_allocation', {}),
            'total_holdings': self.processed_data.get('portfolio_summary', {}).get('total_holdings', 0)
        }
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.processed_data.get('performance_summary', {})
    
    def get_risk_data(self) -> Dict[str, Any]:
        """Get risk metrics"""
        return self.processed_data.get('risk_summary', {})
    
    def prepare_data_for_ai(self) -> str:
        """Prepare structured data summary for AI analysis"""
        summary = []
        
        # Portfolio overview
        portfolio = self.get_portfolio_summary()
        if portfolio:
            summary.append(f"=== PORTFOLIO OVERVIEW ===")
            summary.append(f"Portfolio: {portfolio.get('fund_name', 'Unknown')}")
            summary.append(f"AUM: {portfolio.get('total_aum', 0):,.0f} {portfolio.get('base_currency', 'INR')}")
            summary.append(f"Target Return: {portfolio.get('target_return', 0):.1%}")
            summary.append(f"Risk Level: {portfolio.get('risk_level', 'Unknown')}")
            summary.append(f"Total Holdings: {portfolio.get('total_holdings', 0)}")
            summary.append("")
        
        # Performance
        performance = self.get_performance_data()
        if performance:
            summary.append(f"=== PERFORMANCE METRICS ===")
            summary.append(f"Current Value: {performance.get('current_value', 0):,.0f}")
            summary.append(f"Total Return: {performance.get('total_return', 0):.2%}")
            summary.append(f"Volatility: {performance.get('volatility', 0):.2%}")
            summary.append(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
            summary.append("")
        
        # Risk metrics
        risk = self.get_risk_data()
        if risk:
            summary.append(f"=== RISK METRICS ===")
            summary.append(f"Portfolio Beta: {risk.get('portfolio_beta', 0):.2f}")
            summary.append(f"VaR (95%): {risk.get('var_95', 0):,.0f}")
            summary.append(f"Tracking Error: {risk.get('tracking_error', 0):.2%}")
            summary.append("")
        
        # DETAILED HOLDINGS LIST
        holdings = self.get_holdings_data()
        if holdings.get('top_holdings'):
            summary.append(f"=== DETAILED HOLDINGS ({len(holdings['top_holdings'])} companies) ===")
            for i, holding in enumerate(holdings['top_holdings']):
                summary.append(
                    f"{i+1:2d}. {holding.get('Asset_Name', 'Unknown'):<35} "
                    f"| Ticker: {holding.get('Ticker_Symbol', 'N/A'):<15} "
                    f"| Sector: {holding.get('Sector', 'Unknown'):<20} "
                    f"| Weight: {holding.get('Weight_Percent', 0):>6.2%} "
                    f"| Value: ₹{holding.get('Market_Value', 0):>15,.0f} "
                    f"| ESG: {holding.get('ESG_Rating', 'N/A'):<3}"
                )
            summary.append("")
        
        # Sector breakdown
        if holdings.get('sector_allocation'):
            summary.append(f"=== SECTOR ALLOCATION ===")
            total_value = sum(holdings['sector_allocation'].values())
            sorted_sectors = sorted(holdings['sector_allocation'].items(), key=lambda x: x[1], reverse=True)
            for sector, value in sorted_sectors:
                weight = value / total_value if total_value > 0 else 0
                summary.append(f"- {sector:<25}: {weight:>6.1%} (₹{value:>15,.0f})")
            summary.append("")
        
        return "\n".join(summary)
    
    def get_raw_data(self, sheet_name: str) -> pd.DataFrame:
        """Get raw sheet data"""
        return self.data.get(sheet_name, pd.DataFrame())